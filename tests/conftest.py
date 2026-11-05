"""Fonts under test.

The tests shape text with HarfBuzz against real builds. They use the fonts in
dist/ when ``python -m dandan build-all`` has made them (or the directory in
the DANDAN_DIST environment variable), and otherwise build the two they need
into a temporary directory, which takes a few minutes the first time.
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

    def shape(self, text: str, features: dict[str, bool] | None = None, direction: str | None = None) -> list[int]:
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        if direction:
            buffer.direction = direction
        hb.shape(self.font, buffer, features or {})
        return [info.codepoint for info in buffer.glyph_infos]

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


def _font(tmp_path_factory: pytest.TempPathFactory, level: str, stem: str) -> ShapedFont:
    directory = Path(os.environ.get("DANDAN_DIST", ROOT / "dist"))
    if (directory / f"{stem}.ttf").exists() and (directory / f"{stem}.json").exists():
        return _load(directory, stem)
    directory = tmp_path_factory.mktemp("dist")
    build(level=level, out_dir=directory, woff2=False, include_uncommon=True)
    return _load(directory, stem)


@pytest.fixture(scope="session")
def font_all(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return _font(tmp_path_factory, "all", "Dandan")


@pytest.fixture(scope="session")
def font_n5(tmp_path_factory: pytest.TempPathFactory) -> ShapedFont:
    return _font(tmp_path_factory, "N5", "Dandan-N5")
