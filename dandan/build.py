"""Assemble a Dandan font: base font + annotated glyphs + GSUB rules."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from fontTools.ttLib import TTFont

from . import __version__
from .base import load_base
from .dictionary import Annotation, load_dictionary
from .glyphs import Drawer, Layout
from .gsub import LEVELS, Rules, install

MAX_GLYPHS = 65535
# Glyph ids kept free under the hard limit, for safety in later edits.
RESERVE = 64

LEVEL_NAMES = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1, "all": 6}

# Lone kanji kept bare even when the dictionary agrees on a reading: they are
# mostly counters after digits (3日, 5本, 2時) whose reading changes there.
BARE_LONE = set("日月年時本分人匹杯方何後中回点")

AUTHOR = "Alexis MABANZA"


@dataclass
class BuildResult:
    level: str
    family: str
    files: dict[str, Path]
    base_glyphs: int
    budget: int
    candidates: int
    annotated: int
    total_glyphs: int
    first_annotated_gid: int
    ascender: int
    descender: int
    features: dict[str, list[int]]


def _known_levels(level: str) -> list[int]:
    """JLPT levels whose words stay bare: --level N4 hides N5 and N4."""
    threshold = LEVEL_NAMES[level]
    return [lv for lv in LEVELS if lv >= threshold]


def _priority(annotation: Annotation) -> tuple[int, int, int, int, str]:
    """Rank for the glyph budget.

    JLPT words first, then by JMdict frequency weight. Untagged words (weight
    0) follow, those written with level 1 kanji only and shorter ones first,
    as a rough stand-in for frequency.
    """
    rare = sum(1 for c in annotation.run if c not in _LEVEL1)
    return (0 if annotation.level else 1, -annotation.weight, rare, len(annotation.run), annotation.run)


def _jis_level1() -> set[str]:
    chars = set()
    for row in range(0xB0, 0xD0):  # JIS X 0208 rows 16-47: level 1 kanji
        for cell in range(0xA1, 0xFF):
            try:
                chars.add(bytes([row, cell]).decode("euc_jp"))
            except UnicodeDecodeError:
                pass
    return chars


_LEVEL1 = _jis_level1()


def _postscript_name(family: str) -> str:
    return re.sub(r"[^A-Za-z0-9-]", "", family.replace(" ", "")) + "-Regular"


def _set_names(font: TTFont, family: str, level: str) -> None:
    name = font["name"]
    copyright_text = (
        "Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'. "
        f"Furigana glyphs and rules copyright 2026 {AUTHOR}."
    )
    postscript = _postscript_name(family)
    values = {
        0: copyright_text,
        1: family,
        2: "Regular",
        3: f"{__version__};{postscript};level-{level}",
        4: f"{family} Regular",
        5: f"Version {__version__}; furigana level {level}",
        6: postscript,
        8: AUTHOR,
        9: f"Ryoko NISHIZUKA, Paul D. Hunt (Noto Sans JP); furigana build by {AUTHOR}",
        10: "Japanese font with JLPT-level-aware furigana drawn by OpenType ligatures. "
        "Readings come from JMdict and JmdictFurigana (CC BY-SA 4.0).",
        11: "",
        13: "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
        "Reading data derived from JMdict, JmdictFurigana and yomitan-jlpt-vocab is CC BY-SA 4.0.",
        14: "https://openfontlicense.org",
    }
    for name_id in (7, 11, 16, 17, 21, 22, 25):
        name.removeNames(nameID=name_id)
    name.names = [n for n in name.names if n.nameID < 256 or n.nameID in _referenced_name_ids(font)]
    for name_id, text in values.items():
        if text:
            name.setName(text, name_id, 3, 1, 0x409)
            if name_id <= 6:
                name.setName(text, name_id, 1, 0, 0)
    font["head"].fontRevision = float(__version__.rsplit(".", 1)[0])
    font["OS/2"].achVendID = "NONE"


def _referenced_name_ids(font: TTFont) -> set[int]:
    ids: set[int] = set()
    for record in font["GSUB"].table.FeatureList.FeatureRecord:
        params = record.Feature.FeatureParams
        if params is not None and hasattr(params, "UINameID"):
            ids.add(params.UINameID)
    return ids


def _set_metrics(font: TTFont, first: int) -> tuple[int, int]:
    """Raise the ascender so that the furigana fit inside the line."""
    glyf = font["glyf"]
    order = font.getGlyphOrder()
    top = max((getattr(glyf[name], "yMax", 0) for name in order[first:]), default=0)
    ascender = max(font["hhea"].ascent, ((top + 20 + 9) // 10) * 10)
    descender = font["hhea"].descent  # negative
    hhea, os2 = font["hhea"], font["OS/2"]
    hhea.ascent, hhea.descent, hhea.lineGap = ascender, descender, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = ascender, descender, 0
    os2.usWinAscent, os2.usWinDescent = ascender, -descender
    os2.fsSelection |= 1 << 7  # USE_TYPO_METRICS
    return ascender, descender


def build(
    level: str = "all",
    family: str | None = None,
    out_dir: Path = Path("dist"),
    max_words: int | None = None,
    include_uncommon: bool = True,
    layout: Layout = Layout(),
    weight: int = 400,
    furigana_weight: int = 600,
    woff2: bool = True,
) -> BuildResult:
    if level not in LEVEL_NAMES:
        raise ValueError(f"unknown level {level!r}; expected one of {', '.join(LEVEL_NAMES)}")
    family = family or ("Dandan" if level == "all" else f"Dandan {level}")
    log = lambda message: print(message, file=sys.stderr)  # noqa: E731

    annotations, report = load_dictionary(include_uncommon)
    font = load_base(weight, furigana_weight)
    base_glyphs = len(font.getGlyphOrder())
    budget = MAX_GLYPHS - RESERVE - base_glyphs
    if max_words is not None:
        budget = min(budget, max_words)
    candidates = [a for a in annotations if a.default or a.contexts]
    candidates.sort(key=_priority)
    log(f"glyph budget: {MAX_GLYPHS} max - {base_glyphs} base glyphs - {RESERVE} reserved = "
        f"{MAX_GLYPHS - RESERVE - base_glyphs} annotated glyphs available")
    log(f"dictionary: {len(candidates)} candidate glyphs ({len(report['ambiguous'])} ambiguous runs left bare)")

    drawer = Drawer(font, layout)
    rules = Rules()
    known = _known_levels(level)
    annotated = 0
    skipped: list[str] = []
    for annotation in candidates:
        if annotated >= budget:
            break
        lone = len(annotation.run) == 1
        if lone and annotation.run in BARE_LONE and not annotation.contexts:
            continue
        name = f"fu{annotated:05d}"
        base = drawer.draw(annotation, name)
        if base is None:
            skipped.append(annotation.run)
            continue
        annotated += 1
        if not lone:
            rules.ligatures[tuple(base)] = name
        else:
            if annotation.default and annotation.run not in BARE_LONE:
                rules.lone[base[0]] = name
            for context in annotation.contexts:
                next_glyph = drawer.cmap.get(ord(context))
                if next_glyph is not None:
                    rules.contextual.setdefault(base[0], {})[next_glyph] = name
        if annotation.level is not None:
            rules.hide[annotation.level][name] = base
    drawer.commit()
    first = base_glyphs
    total = len(font.getGlyphOrder())
    if total > MAX_GLYPHS:
        raise RuntimeError(f"{total} glyphs exceed the OpenType limit of {MAX_GLYPHS}")
    log(f"annotated glyphs: {annotated} (cap {budget}); total glyphs: {total}")

    features = install(font, rules, known)
    ascender, descender = _set_metrics(font, first)
    _set_names(font, family, level)
    font["post"].formatType = 3.0
    font["post"].extraNames, font["post"].mapping = [], {}

    # Every bound is already set (glyphs.Drawer computes the composites' own),
    # so recompute the summary tables once and skip fontTools' per-glyph pass.
    for tag in ("maxp", "hhea", "vhea"):
        if tag in font:
            font[tag].recalc(font)
    font.recalcBBoxes = False

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^A-Za-z0-9-]", "", family.replace(" ", "-"))
    files = {"ttf": out_dir / f"{stem}.ttf"}
    font.save(files["ttf"])
    if woff2:
        files["woff2"] = out_dir / f"{stem}.woff2"
        font.flavor = "woff2"
        font.save(files["woff2"])
    result = BuildResult(
        level=level,
        family=family,
        files=files,
        base_glyphs=base_glyphs,
        budget=budget,
        candidates=len(candidates),
        annotated=annotated,
        total_glyphs=total,
        first_annotated_gid=first,
        ascender=ascender,
        descender=descender,
        features=features,
    )
    manifest = {k: (str(v) if isinstance(v, Path) else v) for k, v in result.__dict__.items()}
    manifest["files"] = {k: str(v) for k, v in files.items()}
    manifest["sizes"] = {k: v.stat().st_size for k, v in files.items()}
    manifest["skipped_unplaceable"] = len(skipped)
    (out_dir / f"{stem}.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return result
