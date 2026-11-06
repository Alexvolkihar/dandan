"""Fonts under test.

The tests shape text with HarfBuzz against real builds. They use the fonts in
dist/ when ``python -m dandan build-all`` has made them (or the directory in
the DANDAN_DIST environment variable), and otherwise build the ones they need
(all and N5, the vertical all and Dandan Duo) into a temporary directory, which
takes a few minutes the first time.

The Duo parity tests also build Dandan and Dandan Vertical capped at the Duo's
words per direction, always into a temporary directory: those references are
the single-direction fonts the Duo must shape exactly like.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import pytest
import uharfbuzz as hb

from dandan.build import build

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ShapedFont:
    path: Path
    first_annotated_gid: int
    font: hb.Font
    # Per direction: (id of its first annotated glyph, number of annotated glyphs).
    ranges: dict[str, tuple[int, int]]

    def _buffer(self, text: str, features: dict[str, bool] | None, direction: str | None) -> hb.Buffer:
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        if direction:
            buffer.direction = direction
        hb.shape(self.font, buffer, features or {})
        return buffer

    def shape(self, text: str, features: dict[str, bool] | None = None, direction: str | None = None) -> list[int]:
        return [info.codepoint for info in self._buffer(text, features, direction).glyph_infos]

    def advances(self, text: str, features: dict[str, bool] | None = None, direction: str | None = None) -> list[int]:
        """Advance of each glyph along the line (y advances are negative going down)."""
        buffer = self._buffer(text, features, direction)
        vertical = buffer.direction in ("ttb", "btt")
        return [p.y_advance if vertical else p.x_advance for p in buffer.glyph_positions]

    def annotated(self, gid: int) -> bool:
        return gid >= self.first_annotated_gid

    def canonical(self, gid: int) -> tuple[str, int]:
        """("base", gid) for a base glyph, (direction, index) for the index-th annotated glyph of a direction.

        Base glyphs have the same ids in every build (the vertical base only adds
        glyphs after the horizontal one's), and each direction draws its words in
        the same order, so equal keys mean the same glyph across fonts.
        """
        for direction, (first, count) in self.ranges.items():
            if first <= gid < first + count:
                return direction, gid - first
        return "base", gid

    def layout(
        self, text: str, features: dict[str, bool] | None = None, direction: str | None = None
    ) -> list[tuple[tuple[str, int], int, int, int, int, int]]:
        """Every glyph as (canonical key, cluster, x advance, y advance, x offset, y offset)."""
        buffer = self._buffer(text, features, direction)
        return [
            (self.canonical(info.codepoint), info.cluster, pos.x_advance, pos.y_advance, pos.x_offset, pos.y_offset)
            for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions)
        ]

    def plain(self, text: str) -> list[int]:
        """Glyphs of the text with every furigana feature off."""
        return self.shape(text, {"calt": False})


def _load(directory: Path, stem: str) -> ShapedFont:
    manifest = json.loads((directory / f"{stem}.json").read_text())
    path = directory / f"{stem}.ttf"
    font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
    first = manifest["first_annotated_gid"]
    # Manifests written before Dandan Duo have one direction and no per-direction ranges
    # (and those before Dandan Vertical, no orientation).
    orientation = manifest.get("orientation", "horizontal")
    first_gids = manifest.get("first_gids") or {orientation: first}
    words = manifest.get("words") or {orientation: manifest["annotated"]}
    ranges = {direction: (gid, words[direction]) for direction, gid in first_gids.items()}
    return ShapedFont(path, first, font, ranges)


def _font(
    tmp_path_factory: pytest.TempPathFactory, level: str, stem: str, orientation: str = "horizontal"
) -> ShapedFont:
    directory = Path(os.environ.get("DANDAN_DIST", ROOT / "dist"))
    if (directory / f"{stem}.ttf").exists() and (directory / f"{stem}.json").exists():
        return _load(directory, stem)
    directory = tmp_path_factory.mktemp("dist")
    build(level=level, orientation=orientation, out_dir=directory, woff2=False, include_uncommon=True)
    return _load(directory, stem)


def capped(tmp_path_factory: pytest.TempPathFactory, level: str, orientation: str, max_words: int) -> ShapedFont:
    """Dandan or Dandan Vertical with at most max_words annotated glyphs, built for the parity tests."""
    directory = tmp_path_factory.mktemp(f"capped-{orientation}-{level}")
    result = build(
        level=level,
        orientation=orientation,
        family=f"Dandan Capped {orientation} {level}",
        out_dir=directory,
        max_words=max_words,
        woff2=False,
        include_uncommon=True,
    )
    return _load(directory, result.files["ttf"].stem)


def duo_stem(level: str) -> str:
    return "Dandan-Duo" if level == "all" else f"Dandan-Duo-{level}"


def duo(tmp_path_factory: pytest.TempPathFactory, level: str) -> ShapedFont:
    return _font(tmp_path_factory, level, duo_stem(level), "both")


@pytest.fixture(scope="session")
def font_all(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return _font(tmp_path_factory, "all", "Dandan")


@pytest.fixture(scope="session")
def font_n5(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return _font(tmp_path_factory, "N5", "Dandan-N5")


@pytest.fixture(scope="session")
def font_vertical(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return _font(tmp_path_factory, "all", "Dandan-Vertical", "vertical")


@pytest.fixture(scope="session")
def font_duo(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return duo(tmp_path_factory, "all")
