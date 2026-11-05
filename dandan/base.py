"""Prepare the base font: subset Noto Sans JP to Japanese needs and instance it.

Noto Sans JP ships on Google Fonts as a variable TrueType font. We keep the
characters a Japanese text needs (kana, the JIS X 0208 repertoire with its
level 1 and level 2 kanji, Latin and punctuation), drop the alternates of
features nobody uses for running text, and pin the weight axis. Every glyph
left over is room for annotated words under the 65,535-glyph limit.

The kana drawn as furigana are copied from a heavier instance of the same
variable font, so they keep their colour once scaled down. The vertical build
also copies the heavier kana's vertical forms (``vert``): small kana sit in the
upper right of their cell and ー turns upright, as in tategaki.
"""

from __future__ import annotations

import io
from functools import cache

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from .fetch import CACHE, require

# Features kept from the base font. aalt, jp78, jp83, jp90, nlck, hist and dlig
# pull thousands of alternates that running text never shows.
KEEP_FEATURES = [
    "ccmp", "locl", "liga", "fwid", "hwid", "pwid", "vert", "vrt2",
    "kern", "palt", "halt", "vhal", "vpal", "vkrn", "mark",
]

# Joyo kanji of 2010 that JIS X 0208 lacks.
JOYO_EXTRA = "𠮟塡剝頰"

FURIGANA_PREFIX = "furi."


def jis_x_0208() -> set[int]:
    """Every character of JIS X 0208 (non-kanji rows, level 1 and level 2 kanji)."""
    chars: set[int] = set()
    for row in range(0xA1, 0xFF):
        for cell in range(0xA1, 0xFF):
            try:
                text = bytes([row, cell]).decode("euc_jp")
            except UnicodeDecodeError:
                continue
            if len(text) == 1:
                chars.add(ord(text))
    return chars


def kana_codepoints() -> set[int]:
    return set(range(0x3041, 0x3097)) | set(range(0x309B, 0x30FF)) | set(range(0x31F0, 0x3200))


def base_codepoints() -> set[int]:
    """The repertoire of the subset font."""
    chars = jis_x_0208() | kana_codepoints()
    chars |= set(range(0x20, 0x7F)) | set(range(0xA0, 0x100))
    chars |= set(range(0x2010, 0x2028)) | set(range(0x2030, 0x205F)) | {0x20AC, 0x2122}
    chars |= set(range(0x3000, 0x3040)) | set(range(0xFF01, 0xFFF0))
    chars |= {ord(c) for c in JOYO_EXTRA}
    return chars


def _subset(font: TTFont, codepoints: set[int]) -> None:
    options = subset.Options()
    options.layout_features = KEEP_FEATURES
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.notdef_outline = True
    options.glyph_names = True
    options.hinting = False
    options.drop_tables += ["BASE", "STAT"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=sorted(codepoints))
    subsetter.subset(font)


def _clone(font: TTFont) -> TTFont:
    buffer = io.BytesIO()
    font.save(buffer)
    buffer.seek(0)
    return TTFont(buffer)


def vertical_forms(font: TTFont) -> dict[str, str]:
    """Glyph -> its ``vert`` alternate, from the single substitutions of that feature."""
    gsub = font["GSUB"].table
    indices: set[int] = set()
    for record in gsub.FeatureList.FeatureRecord:
        if record.FeatureTag == "vert":
            indices.update(record.Feature.LookupListIndex)
    mapping: dict[str, str] = {}
    for index in sorted(indices):
        lookup = gsub.LookupList.Lookup[index]
        for subtable in lookup.SubTable:
            if lookup.LookupType == 7:
                subtable = subtable.ExtSubTable
            if hasattr(subtable, "mapping"):
                for source, target in subtable.mapping.items():
                    mapping.setdefault(source, target)
    return mapping


@cache
def _prepared(weight: int, furigana_weight: int, vertical: bool = False) -> bytes:
    suffix = "-vert" if vertical else ""
    path = CACHE / f"base-w{weight}-f{furigana_weight}{suffix}.ttf"
    if path.exists():
        return path.read_bytes()
    variable = TTFont(require("NotoSansJP-VF.ttf"))
    cmap = variable.getBestCmap()
    _subset(variable, {c for c in base_codepoints() if c in cmap})
    variable = _clone(variable)

    font = instancer.instantiateVariableFont(_clone(variable), {"wght": weight})
    heavy = instancer.instantiateVariableFont(variable, {"wght": furigana_weight})
    _add_furigana_kana(font, heavy, vertical)
    font["post"].formatType = 2.0  # keep glyph names in the cached copy
    font["post"].extraNames = []
    font["post"].mapping = {}

    buffer = io.BytesIO()
    font.save(buffer)
    path.write_bytes(buffer.getvalue())
    return buffer.getvalue()


def _add_furigana_kana(font: TTFont, heavy: TTFont, vertical: bool = False) -> None:
    """Copy the kana outlines of the heavier instance as unencoded glyphs.

    With ``vertical``, the kana's vertical forms are copied too, under
    ``furi.<vertical form name>``: the instances keep the variable font's glyph
    names, but each one is looked up through its own cmap and GSUB anyway.
    """
    cmap = font.getBestCmap()
    heavy_cmap = heavy.getBestCmap()
    order = font.getGlyphOrder()
    glyf, hmtx = font["glyf"], font["hmtx"]
    vmtx = font["vmtx"] if "vmtx" in font else None
    heavy_glyf = heavy["glyf"]
    # (name in this font, name in the heavier instance)
    sources: list[tuple[str, str]] = []
    for code in sorted(kana_codepoints() | {0x30FC}):
        if code in cmap and code in heavy_cmap:
            sources.append((cmap[code], heavy_cmap[code]))
    if vertical:
        forms, heavy_forms = vertical_forms(font), vertical_forms(heavy)
        sources += [
            (forms[name], heavy_forms[heavy_name])
            for name, heavy_name in list(sources)
            if name in forms and heavy_name in heavy_forms
        ]
    for source_name, heavy_name in sources:
        source = heavy_glyf[heavy_name]
        if source.isComposite():
            continue
        name = FURIGANA_PREFIX + source_name
        glyph = source.__class__()
        glyph.__dict__.update(source.__dict__)
        order.append(name)
        glyf.glyphs[name] = glyph
        hmtx.metrics[name] = heavy["hmtx"][heavy_name]
        if vmtx is not None:
            vmtx.metrics[name] = vmtx[source_name]
    font.setGlyphOrder(order)
    glyf.glyphOrder = order


def load_base(weight: int = 400, furigana_weight: int = 600, vertical: bool = False) -> TTFont:
    """Return a fresh copy of the prepared base font (with vertical kana forms for the vertical build)."""
    return TTFont(io.BytesIO(_prepared(weight, furigana_weight, vertical)))
