"""Fonts under test.

The tests shape text with HarfBuzz against real builds. They use the fonts in
dist/ when ``python -m dandan build-all`` has made them (or the directory in
the DANDAN_DIST environment variable), and otherwise build the three they need
(all and N5, plus the vertical all) into a temporary directory, which takes a
few minutes the first time.
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

    def plain(self, text: str) -> list[int]:
        """Glyphs of the text with every furigana feature off."""
        return self.shape(text, {"calt": False})


def _load(directory: Path, stem: str) -> ShapedFont:
    manifest = json.loads((directory / f"{stem}.json").read_text())
    path = directory / f"{stem}.ttf"
    font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
    return ShapedFont(path, manifest["first_annotated_gid"], font)


def _font(
    tmp_path_factory: pytest.TempPathFactory, level: str, stem: str, orientation: str = "horizontal"
) -> ShapedFont:
    directory = Path(os.environ.get("DANDAN_DIST", ROOT / "dist"))
    if (directory / f"{stem}.ttf").exists() and (directory / f"{stem}.json").exists():
        return _load(directory, stem)
    directory = tmp_path_factory.mktemp("dist")
    build(level=level, orientation=orientation, out_dir=directory, woff2=False, include_uncommon=True)
    return _load(directory, stem)


@pytest.fixture(scope="session")
def font_all(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return _font(tmp_path_factory, "all", "Dandan")


@pytest.fixture(scope="session")
def font_n5(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return _font(tmp_path_factory, "N5", "Dandan-N5")


@pytest.fixture(scope="session")
def font_vertical(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return _font(tmp_path_factory, "all", "Dandan-Vertical", "vertical")
