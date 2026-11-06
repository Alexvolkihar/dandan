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
from .glyphs import Drawer, Layout, VerticalDrawer
from .gsub import LEVELS, Rules, install

MAX_GLYPHS = 65535
# Glyph ids kept free under the hard limit, for safety in later edits.
RESERVE = 64

LEVEL_NAMES = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1, "all": 6}
# "both" is Dandan Duo: the horizontal and the vertical glyphs and rules in one font.
ORIENTATIONS = ("horizontal", "vertical", "both")

# Lone kanji kept bare even when the dictionary agrees on a reading: they are
# mostly counters after digits (3日, 5本, 2時) whose reading changes there.
BARE_LONE = set("日月年時本分人匹杯方何後中回点")

AUTHOR = "Alexis MABANZA"

# Font units kept free beyond the vertical furigana, on each side of a line.
VERTICAL_MARGIN = 40


@dataclass
class BuildResult:
    level: str
    orientation: str
    family: str
    files: dict[str, Path]
    base_glyphs: int
    budget: int  # annotated glyphs allowed per direction
    candidates: int
    annotated: int  # annotated glyphs, both directions together
    total_glyphs: int
    first_annotated_gid: int
    ascender: int
    descender: int
    features: dict[str, list[int]]
    # Per direction ("horizontal", "vertical"): its annotated glyphs and the id of the first one.
    words: dict[str, int]
    first_gids: dict[str, int]


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


FAMILIES = {"horizontal": "Dandan", "vertical": "Dandan Vertical", "both": "Dandan Duo"}


def default_family(level: str, orientation: str = "horizontal") -> str:
    """Dandan, Dandan N4, Dandan Vertical, Dandan Vertical N4, Dandan Duo, Dandan Duo N4."""
    family = FAMILIES[orientation]
    return family if level == "all" else f"{family} {level}"


def _set_names(font: TTFont, family: str, level: str, orientation: str = "horizontal") -> None:
    name = font["name"]
    copyright_text = (
        "Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'. "
        f"Furigana glyphs and rules copyright 2026 {AUTHOR}."
    )
    postscript = _postscript_name(family)
    description = (
        "Japanese font with JLPT-level-aware furigana drawn by OpenType ligatures. "
        "Readings come from JMdict and JmdictFurigana (CC BY-SA 4.0)."
    )
    if orientation == "vertical":
        description = (
            "Japanese font for vertical text (tategaki) with JLPT-level-aware furigana set right of the "
            "kanji by OpenType ligatures. Readings come from JMdict and JmdictFurigana (CC BY-SA 4.0)."
        )
    elif orientation == "both":
        description = (
            "Japanese font with JLPT-level-aware furigana drawn by OpenType ligatures, above the kanji in "
            "horizontal text and right of them in vertical text (tategaki). Readings come from JMdict and "
            "JmdictFurigana (CC BY-SA 4.0)."
        )
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
        10: description,
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


def _set_metrics(font: TTFont, glyphs: list[str]) -> tuple[int, int]:
    """Raise the ascender so that the furigana of these (horizontal) glyphs fit inside the line."""
    glyf = font["glyf"]
    top = max((getattr(glyf[name], "yMax", 0) for name in glyphs), default=0)
    ascender = max(font["hhea"].ascent, ((top + 20 + 9) // 10) * 10)
    descender = font["hhea"].descent  # negative
    hhea, os2 = font["hhea"], font["OS/2"]
    hhea.ascent, hhea.descent, hhea.lineGap = ascender, descender, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = ascender, descender, 0
    os2.usWinAscent, os2.usWinDescent = ascender, -descender
    os2.fsSelection |= 1 << 7  # USE_TYPO_METRICS
    return ascender, descender


def _vertical_reach(font: TTFont, glyphs: list[str]) -> int:
    """How far right of a vertical line's centre these (vertical) glyphs reach."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    return int(max((getattr(glyf[n], "xMax", 0) - hmtx[n][0] / 2 for n in glyphs), default=0))


def _set_vhea(font: TTFont, reach: int) -> None:
    """vhea's ascender (centre line to the right edge) covers the vertical furigana."""
    vhea = font["vhea"]
    vhea.ascent = max(vhea.ascent, ((reach + 9) // 10) * 10)


def _set_vertical_metrics(font: TTFont, glyphs: list[str]) -> tuple[int, int]:
    """Make room for the furigana column on both sides of a vertical line.

    Browsers centre a vertical line on the ideographic em box (y -120 to 880)
    and size ``line-height: normal`` from the ascender and descender, so both
    are set the furigana's reach (plus a margin) away from the em box's centre:
    the normal line then leaves that reach free on each side. vhea's ascender
    (centre line to the right edge) covers the furigana as well.
    """
    reach = _vertical_reach(font, glyphs)
    half = ((reach + VERTICAL_MARGIN + 9) // 10) * 10
    os2 = font["OS/2"]
    centre = (os2.sTypoAscender + os2.sTypoDescender) // 2  # the base font's typo metrics are the em box
    ascender, descender = centre + half, centre - half
    hhea = font["hhea"]
    hhea.ascent, hhea.descent, hhea.lineGap = ascender, descender, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = ascender, descender, 0
    os2.usWinAscent, os2.usWinDescent = ascender, -descender
    os2.fsSelection |= 1 << 7  # USE_TYPO_METRICS
    _set_vhea(font, reach)
    return ascender, descender


def _annotate(
    drawer: Drawer, candidates: list[Annotation], budget: int, prefix: str
) -> tuple[Rules, list[str], list[str]]:
    """Draw the first ``budget`` placeable candidates; return their rules, glyph names and the skipped runs."""
    vertical = isinstance(drawer, VerticalDrawer)
    # In vertical text the base font's vert lookups run first, so a kana after
    # a kanji is already in its vertical form when the okurigana rules look at it.
    next_forms = drawer.vert if isinstance(drawer, VerticalDrawer) else {}
    rules = Rules()
    names: list[str] = []
    skipped: list[str] = []
    for annotation in candidates:
        if len(names) >= budget:
            break
        lone = len(annotation.run) == 1
        if lone and annotation.run in BARE_LONE and not annotation.contexts:
            continue
        name = f"{prefix}{len(names):05d}"
        base = drawer.draw(annotation, name)
        if base is None:
            skipped.append(annotation.run)
            continue
        names.append(name)
        if not lone:
            rules.ligatures[tuple(base)] = name
        else:
            if annotation.default and annotation.run not in BARE_LONE:
                rules.lone[base[0]] = name
            for context in annotation.contexts:
                next_glyph = drawer.cmap.get(ord(context))
                if next_glyph is not None:
                    next_glyph = next_forms.get(next_glyph, next_glyph)
                    rules.contextual.setdefault(base[0], {})[next_glyph] = name
        if annotation.level is not None:
            rules.hide[annotation.level][name] = base
        elif vertical:
            rules.unlisted[name] = base
    drawer.commit()
    return rules, names, skipped


def build(
    level: str = "all",
    orientation: str = "horizontal",
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
    if orientation not in ORIENTATIONS:
        raise ValueError(f"unknown orientation {orientation!r}; expected one of {', '.join(ORIENTATIONS)}")
    directions = ("horizontal", "vertical") if orientation == "both" else (orientation,)
    family = family or default_family(level, orientation)
    log = lambda message: print(message, file=sys.stderr)  # noqa: E731

    annotations, report = load_dictionary(include_uncommon)
    font = load_base(weight, furigana_weight, "vertical" in directions)
    base_glyphs = len(font.getGlyphOrder())
    available = MAX_GLYPHS - RESERVE - base_glyphs
    # Dandan Duo draws every word twice, once per direction, so each direction gets half the glyphs.
    budget = available // len(directions)
    if max_words is not None:
        budget = min(budget, max_words)
    candidates = [a for a in annotations if a.default or a.contexts]
    candidates.sort(key=_priority)
    log(f"glyph budget: {MAX_GLYPHS} max - {base_glyphs} base glyphs - {RESERVE} reserved = "
        f"{available} annotated glyphs available, {budget} per direction")
    log(f"dictionary: {len(candidates)} candidate glyphs ({len(report['ambiguous'])} ambiguous runs left bare)")

    rules: dict[str, Rules] = {}
    glyphs: dict[str, list[str]] = {}
    first_gids: dict[str, int] = {}
    skipped: list[str] = []
    for direction in directions:
        # One drawer at a time: each copies the glyph order and commits it back when done.
        first_gids[direction] = len(font.getGlyphOrder())
        drawer = VerticalDrawer(font, layout) if direction == "vertical" else Drawer(font, layout)
        # The Duo's vertical glyphs get their own prefix, so no name is drawn twice.
        prefix = "fv" if direction == "vertical" and len(directions) == 2 else "fu"
        rules[direction], glyphs[direction], missed = _annotate(drawer, candidates, budget, prefix)
        skipped += missed
    annotated = sum(len(names) for names in glyphs.values())
    first = base_glyphs
    total = len(font.getGlyphOrder())
    if total > MAX_GLYPHS:
        raise RuntimeError(f"{total} glyphs exceed the OpenType limit of {MAX_GLYPHS}")
    words = {direction: len(names) for direction, names in glyphs.items()}
    log(f"annotated glyphs: {words} (cap {budget} per direction); total glyphs: {total}")

    features = install(font, _known_levels(level), rules.get("horizontal"), rules.get("vertical"))
    if "horizontal" in directions:
        # Dandan Duo keeps Dandan's line metrics, so horizontal text sits exactly as in Dandan;
        # vertical lines are centred on the em box whatever the ascender, and vhea covers the readings.
        ascender, descender = _set_metrics(font, glyphs["horizontal"])
        if "vertical" in directions:
            _set_vhea(font, _vertical_reach(font, glyphs["vertical"]))
    else:
        ascender, descender = _set_vertical_metrics(font, glyphs["vertical"])
    _set_names(font, family, level, orientation)
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
        orientation=orientation,
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
        words=words,
        first_gids=first_gids,
    )
    manifest = {k: (str(v) if isinstance(v, Path) else v) for k, v in result.__dict__.items()}
    manifest["files"] = {k: str(v) for k, v in files.items()}
    manifest["sizes"] = {k: v.stat().st_size for k, v in files.items()}
    manifest["skipped_unplaceable"] = len(skipped)
    (out_dir / f"{stem}.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return result
