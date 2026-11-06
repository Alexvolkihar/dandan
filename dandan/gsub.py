"""Build the furigana lookups and splice them into the base font's GSUB.

Lookup order (OpenType applies lookups in LookupList order):

1. ``words``: ligatures of two or more kanji -> annotated glyph. Within a
   ligature set the longest sequence is tried first, so 日本語 wins over 日本.
2. ``okurigana``: a kanji still alone, followed by a given kana, takes the
   reading that word uses (食 before べ -> 食 with た). Browsers shape kanji and
   kana in separate runs, so this only fires in shapers that see whole words.
3. ``kanji``: a kanji still alone takes its one unambiguous reading.
4. ``hide N5`` .. ``hide N1``: multiple substitutions that turn the annotated
   glyph of a word on that JLPT list back into its plain kanji. Because they run
   after the ligatures, a known word still wins the longest match, so its
   kanji are never annotated one by one.

Features: ``calt`` holds 1-3 plus the hide lookups baked in by ``--level``;
``ss05`` hides N5 words, ``ss04`` N5+N4, ... ``ss01`` every JLPT word.
Turning ``calt`` off turns every furigana off.

The vertical build hangs the same lookups on ``vert`` and ``vrt2`` instead of
``calt``: shapers apply ``vert`` in vertical text only, and ``calt`` in
horizontal text only, so the font annotates vertical text and leaves
horizontal text plain. ``calt`` off cannot switch furigana off there, so the
vertical build adds ``ss10``, which hides every reading (a fifth hide lookup
covers the words on no JLPT list).

Dandan Duo (``--orientation both``) carries both sets: the horizontal lookups
on ``calt`` and the vertical ones on ``vert``/``vrt2``, each over its own
glyphs, so the shaper picks the right set from the text's direction.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from fontTools.otlLib import builder as otl
from fontTools.otlLib.maxContextCalc import maxCtxFont
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot

LEVELS = (5, 4, 3, 2, 1)
CHUNK = 1500  # first glyphs per ligature subtable, to stay clear of offset overflow


@dataclass
class Rules:
    ligatures: dict[tuple[str, ...], str] = field(default_factory=dict)
    lone: dict[str, str] = field(default_factory=dict)
    contextual: dict[str, dict[str, str]] = field(default_factory=dict)  # kanji -> {next glyph: out}
    hide: dict[int, dict[str, list[str]]] = field(default_factory=lambda: {lv: {} for lv in LEVELS})
    unlisted: dict[str, list[str]] = field(default_factory=dict)  # words on no JLPT list


def _lookup(subtables: list, lookup_type: int) -> ot.Lookup:
    lookup = ot.Lookup()
    lookup.LookupType = lookup_type
    lookup.LookupFlag = 0
    lookup.SubTable = subtables
    lookup.SubTableCount = len(subtables)
    return lookup


def _ligature_lookup(ligatures: dict[tuple[str, ...], str]) -> ot.Lookup:
    by_first: dict[str, dict[tuple[str, ...], str]] = {}
    for components, glyph in ligatures.items():
        by_first.setdefault(components[0], {})[components] = glyph
    firsts = sorted(by_first)
    subtables = []
    for start in range(0, len(firsts), CHUNK):
        chunk: dict[tuple[str, ...], str] = {}
        for first in firsts[start:start + CHUNK]:
            chunk.update(by_first[first])
        subtables.append(otl.buildLigatureSubstSubtable(chunk))
    return _lookup(subtables, 4)


def _multiple_lookup(mapping: dict[str, list[str]]) -> ot.Lookup:
    """Multiple substitutions in subtables of CHUNK glyphs (one big one overflows its offsets)."""
    items = sorted(mapping.items())
    subtables = [
        otl.buildMultipleSubstSubtable(dict(items[start:start + CHUNK])) for start in range(0, len(items), CHUNK)
    ]
    return _lookup(subtables, 2)


def _contextual_lookups(
    contextual: dict[str, dict[str, str]], glyph_map: dict[str, int], first_index: int
) -> tuple[ot.Lookup, list[ot.Lookup]]:
    """A chain lookup plus the single substitutions it calls, one per layer."""
    layers: list[dict[str, str]] = []
    rules: dict[str, list[tuple[str, int]]] = {}
    for kanji, by_next in contextual.items():
        outputs = sorted(set(by_next.values()))
        for next_glyph, out in by_next.items():
            layer = outputs.index(out)
            while len(layers) <= layer:
                layers.append({})
            layers[layer][kanji] = out
            rules.setdefault(kanji, []).append((next_glyph, first_index + 1 + layer))
    subtable = ot.ChainContextSubst()
    subtable.Format = 1
    subtable.Coverage = otl.buildCoverage(rules, glyph_map)
    subtable.ChainSubRuleSet = []
    for kanji in subtable.Coverage.glyphs:
        rule_set = ot.ChainSubRuleSet()
        rule_set.ChainSubRule = []
        for next_glyph, lookup_index in sorted(rules[kanji]):
            rule = ot.ChainSubRule()
            rule.Backtrack, rule.BacktrackGlyphCount = [], 0
            rule.Input, rule.InputGlyphCount = [], 1
            rule.LookAhead, rule.LookAheadGlyphCount = [next_glyph], 1
            record = ot.SubstLookupRecord()
            record.SequenceIndex, record.LookupListIndex = 0, lookup_index
            rule.SubstLookupRecord, rule.SubstCount = [record], 1
            rule_set.ChainSubRule.append(rule)
        rule_set.ChainSubRuleCount = len(rule_set.ChainSubRule)
        subtable.ChainSubRuleSet.append(rule_set)
    subtable.ChainSubRuleSetCount = len(subtable.ChainSubRuleSet)
    chain = _lookup([subtable], 6)
    singles = [_lookup([otl.buildSingleSubstSubtable(layer)], 1) for layer in layers]
    return chain, singles


def _feature(tag: str, lookups: list[int], params: ot.FeatureParams | None = None) -> ot.FeatureRecord:
    feature = ot.Feature()
    feature.FeatureParams = params
    feature.LookupListIndex = sorted(lookups)
    feature.LookupCount = len(lookups)
    record = ot.FeatureRecord()
    record.FeatureTag = tag
    record.Feature = feature
    return record


def _stylistic_set_params(font: TTFont, label: str) -> ot.FeatureParamsStylisticSet:
    params = ot.FeatureParamsStylisticSet()
    params.Version = 0
    params.UINameID = font["name"].addMultilingualName({"en": label}, ttFont=font, minNameID=256)
    return params


VERTICAL_FEATURES = ("vert", "vrt2")
HIDE_ALL = "ss10"


@dataclass
class _Installed:
    """Lookup indices of one direction's rules."""

    annotate: list[int]
    hide: dict[int, int]
    unlisted: int | None


def _append_annotate(lookups: list[ot.Lookup], rules: Rules, glyph_map: dict[str, int]) -> list[int]:
    """Append one direction's words, okurigana and kanji lookups; return the indices its feature lists."""
    annotate: list[int] = []
    lookups.append(_ligature_lookup(rules.ligatures))
    annotate.append(len(lookups) - 1)
    if rules.contextual:
        chain, singles = _contextual_lookups(rules.contextual, glyph_map, len(lookups))
        lookups.append(chain)
        annotate.append(len(lookups) - 1)
        lookups.extend(singles)
    lookups.append(_lookup([otl.buildSingleSubstSubtable(rules.lone)], 1))
    annotate.append(len(lookups) - 1)
    return annotate


def _append_hide(lookups: list[ot.Lookup], rules: Rules, vertical: bool) -> tuple[dict[int, int], int | None]:
    """Append one direction's hide lookups (and, vertical, the off-list one)."""
    hide: dict[int, int] = {}
    for level in LEVELS:
        mapping = rules.hide[level]
        if mapping:
            lookups.append(_lookup([otl.buildMultipleSubstSubtable(mapping)], 2))
            hide[level] = len(lookups) - 1
    unlisted = None
    if vertical and rules.unlisted:
        lookups.append(_multiple_lookup(rules.unlisted))
        unlisted = len(lookups) - 1
    return hide, unlisted


def install(
    font: TTFont, baked_levels: list[int], horizontal: Rules | None = None, vertical: Rules | None = None
) -> dict[str, list[int]]:
    """Append the furigana lookups and features to the font's GSUB.

    With both rule sets (Dandan Duo) the lookup list runs: vertical annotate,
    horizontal annotate, vertical hide, horizontal hide. Each direction keeps
    its own order, and their glyphs are disjoint: each set is reached only
    through its own direction's feature (``calt`` or ``vert``), and the
    stylistic sets list the hide lookups of both, of which only the current
    direction's find anything. Should a page force ``calt`` on in vertical text,
    the vertical words are already formed when the horizontal lookups run, and
    the vertical hide lookups run after both, so the text still shapes as in
    Dandan Vertical.
    """
    if horizontal is None and vertical is None:
        raise ValueError("install needs horizontal rules, vertical rules or both")
    gsub = font["GSUB"].table
    lookups = gsub.LookupList.Lookup
    glyph_map = font.getReverseGlyphMap()
    sets: list[tuple[Rules, bool]] = []  # (rules, vertical), vertical first
    if vertical is not None:
        sets.append((vertical, True))
    if horizontal is not None:
        sets.append((horizontal, False))
    annotate = [_append_annotate(lookups, rules, glyph_map) for rules, _ in sets]
    hides = [_append_hide(lookups, rules, is_vertical) for rules, is_vertical in sets]
    gsub.LookupList.LookupCount = len(lookups)
    installed = [_Installed(a, h, u) for a, (h, u) in zip(annotate, hides)]
    down = installed[0] if vertical is not None else None
    across = installed[-1] if horizontal is not None else None

    def baked(i: _Installed) -> list[int]:
        return i.annotate + [i.hide[lv] for lv in baked_levels if lv in i.hide]

    features: dict[str, list[int]] = {}
    records = []
    if across is not None:
        features["calt"] = baked(across)
        records.append(_feature("calt", features["calt"]))
    if down is not None:
        for tag in VERTICAL_FEATURES:
            features[tag] = baked(down)
            if not _extend_features(gsub, tag, features[tag]):
                records.append(_feature(tag, features[tag]))
    for level in LEVELS:
        tag = f"ss0{level}"
        features[tag] = sorted(i.hide[lv] for i in installed for lv in LEVELS if lv >= level and lv in i.hide)
        label = "Hide furigana of N5 words" if level == 5 else f"Hide furigana of N5-N{level} words"
        records.append(_feature(tag, features[tag], _stylistic_set_params(font, label)))
    if down is not None:
        # Only the vertical rules need it: calt off already hides every horizontal reading.
        features[HIDE_ALL] = sorted(down.hide.values()) + ([down.unlisted] if down.unlisted is not None else [])
        records.append(_feature(HIDE_ALL, features[HIDE_ALL], _stylistic_set_params(font, "Hide all furigana")))
    _add_features(gsub, records)
    font["OS/2"].usMaxContext = maxCtxFont(font)
    return features


def _extend_features(gsub: ot.GSUB, tag: str, lookups: list[int]) -> bool:
    """Append lookups to every existing feature with this tag; False when there is none.

    Two records with one tag in a language system would leave the second
    unused (shapers take the first), so the base font's own ``vert`` grows
    instead. Its lookups come first in the lookup list, so the kana and
    punctuation are already in their vertical forms when the words are matched.
    """
    found = False
    for record in gsub.FeatureList.FeatureRecord:
        if record.FeatureTag == tag:
            record.Feature.LookupListIndex = sorted(set(record.Feature.LookupListIndex) | set(lookups))
            record.Feature.LookupCount = len(record.Feature.LookupListIndex)
            found = True
    return found


def _add_features(gsub: ot.GSUB, records: list[ot.FeatureRecord]) -> None:
    """Add feature records to every script and language, keeping tags sorted."""
    old = gsub.FeatureList.FeatureRecord
    combined = [(r.FeatureTag, i, r) for i, r in enumerate(old)]
    combined += [(r.FeatureTag, len(old) + i, r) for i, r in enumerate(records)]
    combined.sort(key=lambda item: (item[0], item[1]))
    remap = {old_index: new_index for new_index, (_, old_index, _) in enumerate(combined)}
    gsub.FeatureList.FeatureRecord = [r for _, _, r in combined]
    gsub.FeatureList.FeatureCount = len(combined)
    new_indices = [remap[len(old) + i] for i in range(len(records))]

    def update(lang_sys: ot.LangSys | None) -> None:
        if lang_sys is None:
            return
        indices = [remap[i] for i in lang_sys.FeatureIndex] + new_indices
        lang_sys.FeatureIndex = sorted(indices)
        lang_sys.FeatureCount = len(indices)
        if lang_sys.ReqFeatureIndex != 0xFFFF:
            lang_sys.ReqFeatureIndex = remap[lang_sys.ReqFeatureIndex]

    for script in gsub.ScriptList.ScriptRecord:
        update(script.Script.DefaultLangSys)
        for lang in script.Script.LangSysRecord:
            update(lang.LangSys)
