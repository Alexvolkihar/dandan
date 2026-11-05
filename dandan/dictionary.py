"""Compile JMdict + JmdictFurigana + JLPT lists into the font's annotations.

A font only ever sees *Han runs*: browsers itemize text by Unicode script, so
in 食べる the font is shown 食 alone and べる in another run. The dictionary is
therefore built per run:

* every (written form, reading) pair of JMdict is split by JmdictFurigana into
  maximal Han runs with their aligned readings;
* each run collects the readings that common words give it, and keeps one
  reading only when it clearly dominates (otherwise the run stays bare);
* a single-kanji run also records the kana that follow it (okurigana), so a
  contextual rule can pick 食[た]べる when the shaper sees the whole word.

Each kept (run, reading) becomes one annotated glyph. Its JLPT level is the
easiest level of the listed words that use that run with that reading.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .fetch import CACHE, require

DICTIONARY_VERSION = 6

# A reading must weigh this many times more than the next one to be kept.
DOMINANCE = 3.0

COMMON_TAGS = {"news1", "ichi1", "spec1", "spec2", "gai1"}
SKIP_KANJI_INFO = {"rK", "sK", "oK", "iK", "ateji-x"}
SKIP_READING_INFO = {"ok", "sk", "ik", "rk"}

# First kana of the inflecting ending, per conjugation class (dictionary form
# ending -> every first kana a conjugated form can start with).
GODAN_ROWS = {
    "v5k": "かきくけこい",
    "v5k-s": "かきくけこっ",
    "v5g": "がぎぐげごい",
    "v5s": "さしすせそ",
    "v5t": "たちつてとっ",
    "v5n": "なにぬねのん",
    "v5b": "ばびぶべぼん",
    "v5m": "まみむめもん",
    "v5r": "らりるれろっ",
    "v5r-i": "らりるれろっ",
    "v5aru": "らりるれろいっ",
    "v5u": "わいうえおっ",
    "v5u-s": "わいうえおっ",
}
ICHIDAN_ENDINGS = "るれろよたてなまずさら"
ADJ_I_ENDINGS = "いくかけさそ"


def is_han(char: str) -> bool:
    """Characters of the Han script, the ones a browser puts in a Han run."""
    code = ord(char)
    return (
        0x4E00 <= code <= 0x9FFF
        or 0x3400 <= code <= 0x4DBF
        or 0xF900 <= code <= 0xFAFF
        or 0x20000 <= code <= 0x3134F
        or char in "々〇"
    )


def is_kana(char: str) -> bool:
    code = ord(char)
    return 0x3041 <= code <= 0x309F or 0x30A0 <= code <= 0x30FF


def priority_score(tags: set[str]) -> int:
    """Map JMdict priority tags to a frequency weight (0 when untagged)."""
    score = 0
    for tag in tags:
        if tag.startswith("nf") and tag[2:].isdigit():
            score += 49 - int(tag[2:])
    score += 20 * ("ichi1" in tags) + 10 * ("news1" in tags) + 10 * ("spec1" in tags)
    score += 5 * ("spec2" in tags) + 5 * ("gai1" in tags)
    score += 2 * len(tags & {"news2", "ichi2", "gai2"})
    return score


@dataclass
class Pair:
    """One written form with one of its readings, from one JMdict entry."""

    seq: int
    kanji: str
    reading: str
    order: int
    weight: int
    common: bool
    pos: tuple[str, ...]
    level: int | None = None


@dataclass
class Occurrence:
    run: str
    reading: str
    following: str
    parts: tuple[tuple[str, str], ...]
    pair: Pair


@dataclass
class Annotation:
    """One annotated glyph: a Han run drawn with its reading above it."""

    run: str
    reading: str
    weight: int
    level: int | None
    default: bool
    contexts: list[str] = field(default_factory=list)
    words: list[str] = field(default_factory=list)
    parts: list[list[str]] = field(default_factory=list)


_ENTITY = re.compile(rb"&(?!amp;|lt;|gt;|quot;|apos;)([\w-]+);")


def _parse_jmdict(path: Path) -> list[Pair]:
    # JMdict codes such as v5k or adj-i are XML entities; keep their names
    # instead of letting the parser expand them to English descriptions.
    with gzip.open(path, "rb") as handle:
        raw = _ENTITY.sub(rb"\1", handle.read())
    pairs: list[Pair] = []
    with io.BytesIO(raw) as handle:
        for _, element in ET.iterparse(handle, events=("end",)):
            if element.tag != "entry":
                continue
            seq = int(element.findtext("ent_seq") or "0")
            pos = tuple(sorted({p.text or "" for p in element.iter("pos")}))
            kanji_forms = []
            for k_ele in element.findall("k_ele"):
                info = {i.text for i in k_ele.findall("ke_inf")}
                if info & SKIP_KANJI_INFO:
                    continue
                tags = {p.text or "" for p in k_ele.findall("ke_pri")}
                kanji_forms.append((k_ele.findtext("keb") or "", tags))
            for order, r_ele in enumerate(element.findall("r_ele")):
                if r_ele.find("re_nokanji") is not None:
                    continue
                if {i.text for i in r_ele.findall("re_inf")} & SKIP_READING_INFO:
                    continue
                reading = r_ele.findtext("reb") or ""
                restrict = {r.text for r in r_ele.findall("re_restr")}
                r_tags = {p.text or "" for p in r_ele.findall("re_pri")}
                for kanji, k_tags in kanji_forms:
                    if restrict and kanji not in restrict:
                        continue
                    common = bool(k_tags & COMMON_TAGS) and bool(r_tags & COMMON_TAGS)
                    weight = min(priority_score(k_tags), priority_score(r_tags))
                    pairs.append(Pair(seq, kanji, reading, order, weight, common, pos))
            element.clear()
    return pairs


def _load_furigana(path: Path) -> dict[tuple[str, str], list[dict[str, str]]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return {(item["text"], item["reading"]): item["furigana"] for item in data}


def _load_jlpt() -> dict[tuple[int, str, str], int]:
    """Map (JMdict seq, written form, reading) to its JLPT level (5 = N5).

    A row without a JMdict id is keyed with seq 0 and matched on form and reading.
    """
    levels: dict[tuple[int, str, str], int] = {}
    for level in (1, 2, 3, 4, 5):
        with require(f"jlpt-n{level}.csv").open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if not row["kanji"]:
                    continue
                key = (int(row["jmdict_seq"] or 0), row["kanji"], row["kana"])
                levels[key] = max(levels.get(key, 0), level)
    return levels


Run = tuple[str, str, str, tuple[tuple[str, str], ...]]


def split_runs(segments: list[dict[str, str]]) -> list[Run] | None:
    """Split a furigana segmentation into Han runs.

    Each run is (text, reading, following kana, per-segment parts). Returns
    None when a reading cannot be placed over Han characters alone.
    """
    tokens: list[list] = []  # ["run", text, reading, parts] or ["lit", text]
    for segment in segments:
        ruby, rt = segment["ruby"], segment.get("rt")
        if rt and all(is_han(c) for c in ruby):
            if tokens and tokens[-1][0] == "run":
                tokens[-1][1] += ruby
                tokens[-1][2] += rt
                tokens[-1][3].append((ruby, rt))
            else:
                tokens.append(["run", ruby, rt, [(ruby, rt)]])
        elif any(is_han(c) for c in ruby):
            return None
        elif tokens and tokens[-1][0] == "lit":
            tokens[-1][1] += ruby
        else:
            tokens.append(["lit", ruby])
    runs: list[Run] = []
    for index, token in enumerate(tokens):
        if token[0] != "run":
            continue
        following = ""
        if index + 1 < len(tokens) and all(is_kana(c) for c in tokens[index + 1][1]):
            following = tokens[index + 1][1]
        runs.append((token[1], token[2], following, tuple(token[3])))
    return runs


def _context_starts(pair: Pair, following: str) -> list[str]:
    """First kana that can follow a single-kanji run, conjugations included."""
    if not following:
        return []
    whole_tail = pair.kanji.endswith(following)
    if whole_tail and len(following) == 1:
        for pos in pair.pos:
            if pos in GODAN_ROWS and following in GODAN_ROWS[pos]:
                return list(GODAN_ROWS[pos])
            if pos == "v1" and following == "る":
                return list(ICHIDAN_ENDINGS)
            if pos == "adj-i" and following == "い":
                return list(ADJ_I_ENDINGS)
        if any(p.startswith(("v", "adj")) for p in pair.pos):
            return []
    return [following[0]]


def _choose(readings: dict[str, tuple[int, int, int]]) -> str | None:
    """Pick a dominant reading from {reading: (weight, entries, order)}."""
    ranked = sorted(readings.items(), key=lambda item: (-item[1][0], item[1][2]))
    if not ranked:
        return None
    if len(ranked) == 1:
        return ranked[0][0]
    best, second = ranked[0][1][0], ranked[1][1][0]
    if best >= DOMINANCE * max(second, 1):
        return ranked[0][0]
    return None


def _candidates(occurrences: list[Occurrence]) -> dict[str, tuple[int, int, int]]:
    """Reduce occurrences to one preferred reading per JMdict entry."""
    # Inside one entry, JMdict lists the everyday reading first (今日: きょう
    # before こんにち), so the order wins over the newspaper frequency; a
    # reading on an easier JLPT list wins over both.
    per_entry: dict[int, Occurrence] = {}
    entry_weight: dict[int, int] = defaultdict(int)
    for occ in occurrences:
        entry_weight[occ.pair.seq] = max(entry_weight[occ.pair.seq], occ.pair.weight)
        current = per_entry.get(occ.pair.seq)
        key = (-(occ.pair.level or 0), occ.pair.order)
        if current is None or key < (-(current.pair.level or 0), current.pair.order):
            per_entry[occ.pair.seq] = occ
    readings: dict[str, tuple[int, int, int]] = {}
    for seq, occ in per_entry.items():
        weight, entries, order = readings.get(occ.reading, (0, 0, 1 << 30))
        readings[occ.reading] = (max(weight, entry_weight[seq]), entries + 1, min(order, occ.pair.order))
    return readings


AFFIX_POS = {"suf", "pref", "ctr"}


def _affix_conflict(occurrences: list[Occurrence], chosen: str) -> bool:
    """A lone kanji is often a suffix or counter after another word (東京都,
    三本): if a common affix reading differs from the chosen one, the font
    cannot tell which applies, so the kanji stays bare."""
    return any(
        occ.reading != chosen and occ.pair.common and not occ.following and set(occ.pair.pos) & AFFIX_POS
        for occ in occurrences
    )


def compile_dictionary(include_uncommon: bool = False) -> tuple[list[Annotation], dict[str, list[str]]]:
    """Build every annotation the font can use, plus a report of skipped runs."""
    pairs = _parse_jmdict(require("JMdict_e.gz"))
    furigana = _load_furigana(require("JmdictFurigana.json"))
    jlpt = _load_jlpt()

    by_run: dict[str, list[Occurrence]] = defaultdict(list)
    for pair in pairs:
        pair.level = jlpt.get((pair.seq, pair.kanji, pair.reading)) or jlpt.get((0, pair.kanji, pair.reading))
        if pair.level is not None and not pair.common:
            pair.common = True
            pair.weight = max(pair.weight, 10)
        if not (pair.common or include_uncommon):
            continue
        segments = furigana.get((pair.kanji, pair.reading))
        if segments is None:
            continue
        runs = split_runs(segments)
        if runs is None:
            continue
        for run, reading, following, parts in runs:
            by_run[run].append(Occurrence(run, reading, following, parts, pair))

    annotations: list[Annotation] = []
    ambiguous: list[str] = []
    for run, occurrences in by_run.items():
        chosen = _choose(_candidates(occurrences))
        if chosen is not None and len(run) == 1 and _affix_conflict(occurrences, chosen):
            chosen = None
        contexts: dict[str, str] = {}
        if len(run) == 1:
            by_context: dict[str, list[Occurrence]] = defaultdict(list)
            for occ in occurrences:
                for start in _context_starts(occ.pair, occ.following):
                    by_context[start].append(occ)
            for start, group in by_context.items():
                picked = _choose(_candidates(group))
                if picked is not None:
                    contexts[start] = picked
        if chosen is None:
            ambiguous.append(run)
        readings = {chosen} if chosen else set()
        readings |= set(contexts.values())
        for reading in sorted(readings):
            support = sorted(
                (o for o in occurrences if o.reading == reading),
                key=lambda o: (-o.pair.weight, o.pair.seq),
            )
            levels = [o.pair.level for o in support if o.pair.level is not None]
            annotations.append(
                Annotation(
                    run=run,
                    reading=reading,
                    weight=max(o.pair.weight for o in support),
                    level=max(levels) if levels else None,
                    default=reading == chosen,
                    contexts=sorted(c for c, r in contexts.items() if r == reading and reading != chosen),
                    words=sorted({o.pair.kanji for o in support})[:5],
                    parts=[list(p) for p in support[0].parts],
                )
            )
    annotations.sort(key=lambda a: (a.run, a.reading))
    return annotations, {"ambiguous": sorted(ambiguous)}


def load_dictionary(include_uncommon: bool = False) -> tuple[list[Annotation], dict[str, list[str]]]:
    """Return the compiled dictionary, from the cache when it is up to date."""
    suffix = "-all" if include_uncommon else ""
    path = CACHE / f"dictionary-v{DICTIONARY_VERSION}{suffix}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Annotation(**a) for a in data["annotations"]], data["report"]
    annotations, report = compile_dictionary(include_uncommon)
    payload = {"annotations": [asdict(a) for a in annotations], "report": report}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return annotations, report
