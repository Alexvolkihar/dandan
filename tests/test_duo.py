"""Dandan Duo: Dandan in horizontal text and Dandan Vertical in vertical text, in one font.

The Duo has room for half as many words per direction (both sets of glyphs
share the 65,535-glyph limit), so it is compared with Dandan and Dandan
Vertical built with the same cap: those draw the same words in the same
order, and the Duo must shape every sentence exactly like them, glyph for
glyph and position for position, at every level and with every switch.

DANDAN_PARITY_LEVELS (default "all,N4") picks the baked-in levels compared;
"all,N5,N4,N3,N2,N1" checks every one (a Duo and two references per level).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import cache

import pytest
from fontTools.ttLib import TTFont

from conftest import ShapedFont, capped, duo
from dandan.base import load_base
from dandan.build import MAX_GLYPHS, RESERVE

TTB = "ttb"

CORPUS = [
    "今日は図書館で日本語の勉強をします。",
    "経済の状況は複雑ですが、政府は対策を検討しています。",
    "学生と先生が教室で話している。",
    "東京都に住んでいる友達に手紙を書きました。",
    "食べる、飲む、見る、行く、来る、話す、読む。",
    "3日に5本のペンを買って、2時に駅で会いましょう。",
    "彼女は毎朝コーヒーを飲みながら新聞を読む。",
    "この問題について、もう一度よく考えてみてください。",
    "人気のある店の前には、いつも長い行列ができている。",
    "地震の後、交通機関は一時的に運転を見合わせた。",
    "環境保護と経済成長の両立は、現代社会の重要な課題だ。",
    "明日の天気予報によると、午後から雨が降るそうです。",
    "子供たちは公園で元気に遊んでいます。",
    "彼は医者になるために、毎日一生懸命勉強している。",
    "日本、中国、韓国。 Latin text 123, and ＡＢＣ　全角スペース。",
    "「本当ですか？」と彼は驚いた顔で聞いた――信じられない。",
    "ラーメン屋の店主は、朝早くからスープを仕込む。",
    "鬱蒼とした森の奥に、古い神社が佇んでいる。",
    "憂鬱な気分を吹き飛ばすような、爽やかな風が吹いた。",
    "量子力学における不確定性原理は、観測の限界を示す。",
    "日",
    "日本",
    "日本語",
    "食",
    "都",
]

SETTINGS: list[dict[str, bool]] = [
    {},
    {"ss05": True},
    {"ss04": True},
    {"ss03": True},
    {"ss02": True},
    {"ss01": True},
    {"ss10": True},
    {"calt": False},
    {"calt": False, "ss03": True},
    {"ss05": True, "ss10": True},
    {"ss01": True, "ss10": True},
    {"vert": False},
    {"vert": False, "vrt2": False},
    {"liga": False},
    # Forced on: a no-op in horizontal text; in vertical text the vertical words must still win.
    {"calt": True},
    {"calt": True, "ss05": True},
    {"calt": True, "ss10": True},
]

LEVELS = os.environ.get("DANDAN_PARITY_LEVELS", "all,N4").split(",")


@dataclass
class Trio:
    level: str
    duo: ShapedFont
    horizontal: ShapedFont  # Dandan, capped at the Duo's words per direction
    vertical: ShapedFont  # Dandan Vertical, same cap


@cache
def _ttfont(path) -> TTFont:
    return TTFont(path, lazy=True)


@pytest.fixture(scope="session", params=LEVELS)
def trio(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> Trio:
    level = request.param
    font = duo(tmp_path_factory, level)
    words = font.ranges["horizontal"][1]
    assert font.ranges["vertical"][1] == words
    return Trio(
        level,
        font,
        capped(tmp_path_factory, level, "horizontal", words),
        capped(tmp_path_factory, level, "vertical", words),
    )


def _mismatches(font: ShapedFont, reference: ShapedFont, direction: str | None) -> list[str]:
    found = []
    for features in SETTINGS:
        for text in CORPUS:
            got = font.layout(text, features, direction)
            expected = reference.layout(text, features, direction)
            if got != expected:
                found.append(f"{direction or 'ltr'} {features} {text}: {got} != {expected}")
    return found


def test_horizontal_text_shapes_like_dandan(trio):
    assert _mismatches(trio.duo, trio.horizontal, None) == []


def test_vertical_text_shapes_like_dandan_vertical(trio):
    assert _mismatches(trio.duo, trio.vertical, TTB) == []


def test_the_parity_corpus_gets_furigana_both_ways(trio):
    # Guards against a parity that holds because nothing is annotated at all.
    # 日本語 is on no JLPT list, so no baked level hides it.
    text = CORPUS[0]
    for direction, key in ((None, "horizontal"), (TTB, "vertical")):
        glyphs = [g[0][0] for g in trio.duo.layout(text, direction=direction)]
        assert key in glyphs, direction


def test_each_direction_uses_only_its_own_glyphs(font_duo):
    for text in CORPUS:
        for features in SETTINGS:
            across = {key[0] for key, *_ in font_duo.layout(text, features)}
            down = {key[0] for key, *_ in font_duo.layout(text, features, TTB)}
            assert "vertical" not in across, (text, features)
            assert "horizontal" not in down, (text, features)


def test_words_split_the_glyph_budget(font_duo):
    font = _ttfont(font_duo.path)
    count = len(font.getGlyphOrder())
    assert count < MAX_GLYPHS
    (h_first, h_words), (v_first, v_words) = font_duo.ranges["horizontal"], font_duo.ranges["vertical"]
    base = len(load_base(vertical=True).getGlyphOrder())
    assert h_first == base and v_first == base + h_words
    assert h_words == v_words == (MAX_GLYPHS - RESERVE - base) // 2
    assert count == v_first + v_words


def test_base_glyph_ids_match_both_single_fonts():
    # canonical() relies on it: the vertical base only appends glyphs to the horizontal one.
    horizontal = load_base(vertical=False).getGlyphOrder()
    assert load_base(vertical=True).getGlyphOrder()[: len(horizontal)] == horizontal


def test_line_metrics_are_dandans(trio):
    duo_font, dandan = _ttfont(trio.duo.path), _ttfont(trio.horizontal.path)
    for tag, fields in (
        ("hhea", ("ascent", "descent", "lineGap")),
        ("OS/2", ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent")),
    ):
        for field in fields:
            assert getattr(duo_font[tag], field) == getattr(dandan[tag], field), (tag, field)


def test_vhea_covers_the_vertical_readings(trio):
    duo_font, vertical = _ttfont(trio.duo.path), _ttfont(trio.vertical.path)
    assert duo_font["vhea"].ascent == vertical["vhea"].ascent


def test_family_name(font_duo):
    assert _ttfont(font_duo.path)["name"].getDebugName(1) == "Dandan Duo"
