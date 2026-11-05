"""The vertical build: furigana right of the kanji, in vertical text only."""

from __future__ import annotations

from functools import cache

from fontTools.ttLib import TTFont

from dandan.build import MAX_GLYPHS
from dandan.glyphs import Layout

TTB = "ttb"


@cache
def _ttfont(path) -> TTFont:
    return TTFont(path)


def _glyph(shaped, gid: int):
    font = _ttfont(shaped.path)
    name = font.getGlyphName(gid)
    return font, name, font["glyf"][name]


def test_vertical_word_is_one_ligature(font_vertical):
    glyphs = font_vertical.shape("日本語", direction=TTB)
    assert len(glyphs) == 1 and font_vertical.annotated(glyphs[0])


def test_vertical_advance_is_the_sum_of_the_kanji(font_vertical):
    word = "日本語"
    plain = font_vertical.advances(word, {"ss10": True}, direction=TTB)
    assert len(plain) == 3 and all(a < 0 for a in plain)
    assert font_vertical.advances(word, direction=TTB) == [sum(plain)]


def _split(glyph):
    """Kanji components (unscaled) and kana components (scaled down), in drawing order."""
    kanji = [c for c in glyph.components if not hasattr(c, "transform")]
    kana = [c for c in glyph.components if hasattr(c, "transform")]
    return kanji, kana


def test_furigana_sit_right_of_the_kanji_column(font_vertical):
    gid = font_vertical.shape("今日", direction=TTB)[0]
    font, name, glyph = _glyph(font_vertical, gid)
    advance = font["hmtx"][name][0]
    kanji, kana = _split(glyph)
    assert [c.x for c in kanji] == [0, 0]  # stacked in one column
    assert kanji[0].y > kanji[1].y  # 今 above 日
    assert kana and all(c.x == Layout().column for c in kana)
    assert glyph.xMax > advance  # the reading hangs right of the column
    ys = [c.y for c in kana]
    assert ys == sorted(ys, reverse=True)  # read top to bottom


def test_small_kana_take_their_vertical_forms(font_vertical):
    # 今日 reads きょう: the small ょ sits in the upper right of its cell, not
    # on the baseline at the left as in horizontal text.
    font, _, glyph = _glyph(font_vertical, font_vertical.shape("今日", direction=TTB)[0])
    _, kana = _split(glyph)
    assert len(kana) == 3
    small = font["glyf"][kana[1].glyphName]
    assert small.yMin > 0 and small.xMin > 250


def test_horizontal_text_stays_bare(font_vertical):
    text = "今日は日本語の勉強をします"
    for features in ({}, {"calt": True}):
        glyphs = font_vertical.shape(text, features)
        assert len(glyphs) == len(text)
        assert not any(font_vertical.annotated(g) for g in glyphs)


def test_stylistic_sets_hide_levels_in_vertical_text(font_vertical):
    word = "学生"  # N5
    bare = font_vertical.shape(word, {"ss10": True}, direction=TTB)
    assert len(bare) == 2 and not any(font_vertical.annotated(g) for g in bare)
    assert font_vertical.annotated(font_vertical.shape(word, direction=TTB)[0])
    assert font_vertical.shape(word, {"ss05": True}, direction=TTB) == bare
    hard = "経済"  # N3: kept by ss05, hidden by ss03
    assert font_vertical.annotated(font_vertical.shape(hard, {"ss05": True}, direction=TTB)[0])
    assert not any(font_vertical.annotated(g) for g in font_vertical.shape(hard, {"ss03": True}, direction=TTB))


def test_ss10_hides_every_reading(font_vertical):
    text = "今日は日本語の勉強をします"
    # 日本語 is on no JLPT list: ss01 keeps its reading, ss10 does not.
    assert font_vertical.annotated(font_vertical.shape("日本語", {"ss01": True}, direction=TTB)[0])
    glyphs = font_vertical.shape(text, {"ss10": True}, direction=TTB)
    assert len(glyphs) == len(text)
    assert not any(font_vertical.annotated(g) for g in glyphs)


def test_vertical_punctuation_still_turns(font_vertical):
    across = font_vertical.shape("。ー")
    down = font_vertical.shape("。ー", direction=TTB)
    assert len(down) == 2
    assert across[0] != down[0] and across[1] != down[1]


def test_okurigana_rule_sees_vertical_kana(font_vertical):
    glyphs = font_vertical.shape("食べる", direction=TTB)
    assert len(glyphs) == 3
    assert font_vertical.annotated(glyphs[0])


def test_vertical_glyph_count_under_the_limit(font_vertical):
    assert len(_ttfont(font_vertical.path).getGlyphOrder()) < MAX_GLYPHS
