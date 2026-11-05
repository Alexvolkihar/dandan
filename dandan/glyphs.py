"""Draw annotated glyphs as TrueType composites.

An annotated glyph references the base kanji glyphs side by side and the
furigana kana scaled down above them. Nothing is redrawn: a composite costs a
few bytes per component, which keeps tens of thousands of words affordable.

The vertical build (``VerticalDrawer``) stacks the kanji top to bottom and
sets the kana, upright and in their vertical forms, in a thin column to the
right of them, as Japanese vertical typesetting does.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import (
    ROUND_XY_TO_GRID,
    UNSCALED_COMPONENT_OFFSET,
    Glyph,
    GlyphComponent,
)

from .base import FURIGANA_PREFIX, vertical_forms
from .dictionary import Annotation


@dataclass(frozen=True)
class Layout:
    """Where the furigana go, in font units (1000 per em)."""

    scale: float = 0.5
    baseline: int = 900  # y offset of the scaled kana's own baseline
    overhang: int = 0  # how far a reading may spill past its kanji, per side
    min_x_scale: float = 0.25  # narrower than this and the word stays bare
    # Vertical build: x offset of the kana's (scaled) em box, so the kana sit
    # right of the 1000-unit column, overlapping it as much as the horizontal
    # kana overlap the kanji's em box (900 - 0.5 * 120 = 840, 40 under 880).
    column: int = 960


class Drawer:
    def __init__(self, font: TTFont, layout: Layout) -> None:
        self.font = font
        self.layout = layout
        self.cmap = font.getBestCmap()
        self.glyf = font["glyf"]
        self.hmtx = font["hmtx"]
        self.vmtx = font["vmtx"] if "vmtx" in font else None
        self.order = list(font.getGlyphOrder())
        self.names = set(self.order)

    def base_glyphs(self, text: str) -> list[str] | None:
        names = [self.cmap.get(ord(c)) for c in text]
        if any(n is None for n in names):
            return None
        return [n for n in names if n is not None]

    def kana_glyphs(self, reading: str) -> list[str] | None:
        names = []
        for char in reading:
            name = self.cmap.get(ord(char))
            if name is None:
                return None
            furigana = FURIGANA_PREFIX + name
            names.append(furigana if furigana in self.names else name)
        return names

    def _advance(self, name: str) -> int:
        return self.hmtx[name][0]

    def _place(self, base: list[str], annotation: Annotation) -> list[tuple[str, float, float]] | None:
        """Return (kana glyph, x, x-scale) for every kana of the reading."""
        scale = self.layout.scale
        widths = [self._advance(n) for n in base]
        total = sum(widths)
        # Mono ruby: each segment centred over its own kanji when nothing collides.
        placed: list[tuple[str, float, float]] = []
        cursor, previous_end, mono = 0, float("-inf"), True
        for ruby, rt in annotation.parts:
            span = sum(widths[cursor:cursor + len(ruby)])
            kana = self.kana_glyphs(rt)
            if kana is None:
                return None
            width = sum(self._advance(k) for k in kana) * scale
            start = sum(widths[:cursor]) + (span - width) / 2
            if width > span or start < previous_end - 1:
                mono = False
                break
            x = start
            for k in kana:
                placed.append((k, x, scale))
                x += self._advance(k) * scale
            previous_end = x
            cursor += len(ruby)
        if mono and cursor == len(base):
            return placed
        # Group ruby: the whole reading centred, condensed when it is too long.
        kana = self.kana_glyphs(annotation.reading)
        if kana is None:
            return None
        natural = sum(self._advance(k) for k in kana)
        x_scale = min(scale, (total + 2 * self.layout.overhang) / natural)
        if x_scale < self.layout.min_x_scale:
            return None
        x = (total - natural * x_scale) / 2
        placed = []
        for k in kana:
            placed.append((k, x, x_scale))
            x += self._advance(k) * x_scale
        return placed

    def draw(self, annotation: Annotation, name: str) -> list[str] | None:
        """Add the annotated glyph; return its base glyph names, or None to skip."""
        base = self.base_glyphs(annotation.run)
        if base is None:
            return None
        placed = self._place(base, annotation)
        if placed is None:
            return None
        components = []
        x = 0
        for glyph_name in base:
            components.append(_component(glyph_name, x, 0))
            x += self._advance(glyph_name)
        for glyph_name, kx, x_scale in placed:
            components.append(_component(glyph_name, kx, self.layout.baseline, x_scale, self.layout.scale))
        glyph = Glyph()
        glyph.numberOfContours = -1
        glyph.components = components
        self._set_bounds(glyph)
        self.glyf.glyphs[name] = glyph
        self.order.append(name)
        self.names.add(name)
        self.hmtx.metrics[name] = (x, glyph.xMin)
        if self.vmtx is not None:
            self.vmtx.metrics[name] = (x, max(0, 880 - glyph.yMax))
        return base

    def _set_bounds(self, glyph: Glyph) -> None:
        """Bounds from the components' own boxes: exact for scale-only transforms
        and far cheaper than flattening every outline (fontTools' recalcBounds)."""
        boxes = []
        for component in glyph.components:
            source = self.glyf[component.glyphName]
            if source.numberOfContours == 0:
                continue
            sx, sy = 1.0, 1.0
            if hasattr(component, "transform"):
                sx, sy = component.transform[0][0], component.transform[1][1]
            boxes.append((
                source.xMin * sx + component.x, source.yMin * sy + component.y,
                source.xMax * sx + component.x, source.yMax * sy + component.y,
            ))
        glyph.xMin = math.floor(min(b[0] for b in boxes))
        glyph.yMin = math.floor(min(b[1] for b in boxes))
        glyph.xMax = math.ceil(max(b[2] for b in boxes))
        glyph.yMax = math.ceil(max(b[3] for b in boxes))

    def commit(self) -> None:
        self.font.setGlyphOrder(self.order)
        self.glyf.glyphOrder = self.order


class VerticalDrawer(Drawer):
    """Kanji stacked downwards, the reading in a column to their right.

    A glyph's vertical origin is its first kanji's (yMax + top side bearing,
    880 for nearly every kanji), the kanji follow one vertical advance apart,
    and the vertical advance is their sum. The horizontal advance is the first
    kanji's, so that browsers centre the kanji in the line and the kana hang
    into the space between lines, as ruby does.
    """

    def __init__(self, font: TTFont, layout: Layout) -> None:
        super().__init__(font, layout)
        if self.vmtx is None:
            raise ValueError("the vertical build needs a vmtx table")
        self.vert = vertical_forms(font)

    def kana_glyphs(self, reading: str) -> list[str] | None:
        names = []
        for char in reading:
            name = self.cmap.get(ord(char))
            if name is None:
                return None
            name = self.vert.get(name, name)
            furigana = FURIGANA_PREFIX + name
            names.append(furigana if furigana in self.names else name)
        return names

    def _height(self, name: str) -> int:
        assert self.vmtx is not None
        return self.vmtx[name][0]

    def _origin(self, name: str) -> int:
        """y of the glyph's vertical origin (top of its em box), in its own coordinates.

        A furigana kana keeps the vertical metrics of the regular glyph it was
        copied over, so its origin is read from that glyph.
        """
        assert self.vmtx is not None
        plain = name.removeprefix(FURIGANA_PREFIX)
        if plain in self.names:
            name = plain
        glyph = self.glyf[name]
        top = getattr(glyph, "yMax", 0) if glyph.numberOfContours else 0
        return top + self.vmtx[name][1]

    def _place(self, base: list[str], annotation: Annotation) -> list[tuple[str, float, float]] | None:
        """Return (kana glyph, distance of its em box below the column top, y-scale)."""
        scale = self.layout.scale
        heights = [self._height(n) for n in base]
        total = sum(heights)
        placed: list[tuple[str, float, float]] = []
        cursor, previous_end, mono = 0, float("-inf"), True
        for ruby, rt in annotation.parts:
            span = sum(heights[cursor:cursor + len(ruby)])
            kana = self.kana_glyphs(rt)
            if kana is None:
                return None
            length = sum(self._height(k) for k in kana) * scale
            start = sum(heights[:cursor]) + (span - length) / 2
            if length > span or start < previous_end - 1:
                mono = False
                break
            y = start
            for k in kana:
                placed.append((k, y, scale))
                y += self._height(k) * scale
            previous_end = y
            cursor += len(ruby)
        if mono and cursor == len(base):
            return placed
        kana = self.kana_glyphs(annotation.reading)
        if kana is None:
            return None
        natural = sum(self._height(k) for k in kana)
        y_scale = min(scale, (total + 2 * self.layout.overhang) / natural)
        if y_scale < self.layout.min_x_scale:
            return None
        y = (total - natural * y_scale) / 2
        placed = []
        for k in kana:
            placed.append((k, y, y_scale))
            y += self._height(k) * y_scale
        return placed

    def draw(self, annotation: Annotation, name: str) -> list[str] | None:
        assert self.vmtx is not None
        base = self.base_glyphs(annotation.run)
        if base is None:
            return None
        placed = self._place(base, annotation)
        if placed is None:
            return None
        top = self._origin(base[0])
        components = []
        y = 0
        for glyph_name in base:
            # Each kanji's own origin sits y units below the column top.
            components.append(_component(glyph_name, 0, top - y - self._origin(glyph_name)))
            y += self._height(glyph_name)
        scale = self.layout.scale
        for glyph_name, depth, y_scale in placed:
            dy = top - depth - self._origin(glyph_name) * y_scale
            components.append(_component(glyph_name, self.layout.column, dy, scale, y_scale))
        glyph = Glyph()
        glyph.numberOfContours = -1
        glyph.components = components
        self._set_bounds(glyph)
        self.glyf.glyphs[name] = glyph
        self.order.append(name)
        self.names.add(name)
        self.hmtx.metrics[name] = (self._advance(base[0]), glyph.xMin)
        self.vmtx.metrics[name] = (y, top - glyph.yMax)
        return base


def _component(name: str, x: float, y: float, sx: float = 1.0, sy: float = 1.0) -> GlyphComponent:
    component = GlyphComponent()
    component.glyphName = name
    component.x, component.y = round(x), round(y)
    component.flags = ROUND_XY_TO_GRID | UNSCALED_COMPONENT_OFFSET
    if sx != 1.0 or sy != 1.0:
        component.transform = [[sx, 0.0], [0.0, sy]]
    return component
