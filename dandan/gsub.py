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


def install(font: TTFont, rules: Rules, baked_levels: list[int]) -> dict[str, list[int]]:
    """Append the furigana lookups and features to the font's GSUB."""
    gsub = font["GSUB"].table
    lookups = gsub.LookupList.Lookup
    glyph_map = font.getReverseGlyphMap()

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

    hide_index: dict[int, int] = {}
    for level in LEVELS:
        mapping = rules.hide[level]
        if mapping:
            lookups.append(_lookup([otl.buildMultipleSubstSubtable(mapping)], 2))
            hide_index[level] = len(lookups) - 1
    gsub.LookupList.LookupCount = len(lookups)

    features: dict[str, list[int]] = {
        "calt": annotate + [hide_index[lv] for lv in baked_levels if lv in hide_index]
    }
    records = [_feature("calt", features["calt"])]
    for level in LEVELS:
        tag = f"ss0{level}"
        features[tag] = [hide_index[lv] for lv in LEVELS if lv >= level and lv in hide_index]
        label = "Hide furigana of N5 words" if level == 5 else f"Hide furigana of N5-N{level} words"
        records.append(_feature(tag, features[tag], _stylistic_set_params(font, label)))
    _add_features(gsub, records)
    font["OS/2"].usMaxContext = maxCtxFont(font)
    return features


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
