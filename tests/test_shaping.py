"""Shaping tests: what HarfBuzz actually draws with the built fonts."""

from __future__ import annotations

from fontTools.ttLib import TTFont

from dandan.build import MAX_GLYPHS


def test_kyou_is_one_annotated_ligature(font_all):
    glyphs = font_all.shape("今日")
    assert len(glyphs) == 1
    assert font_all.annotated(glyphs[0])


def test_longest_match_wins(font_all):
    nihongo = font_all.shape("日本語")
    nihon = font_all.shape("日本")
    assert len(nihongo) == 1 and font_all.annotated(nihongo[0])
    assert len(nihon) == 1 and font_all.annotated(nihon[0])
    assert nihongo != nihon  # 日本語 is its own glyph, not 日本 + 語


def test_longest_match_inside_a_sentence(font_all):
    glyphs = font_all.shape("日本語を勉強する")
    assert font_all.annotated(glyphs[0])
    assert glyphs[0] == font_all.shape("日本語")[0]


def test_n5_word_bare_in_n5_build_and_annotated_in_all(font_all, font_n5):
    for word in ("学生", "先生", "今日"):
        annotated = font_all.shape(word)
        assert len(annotated) == 1 and font_all.annotated(annotated[0]), word
        bare = font_n5.shape(word)
        assert bare == font_n5.plain(word), word
        assert not any(font_n5.annotated(g) for g in bare), word


def test_n5_build_still_annotates_harder_words(font_n5):
    glyphs = font_n5.shape("経済")
    assert len(glyphs) == 1 and font_n5.annotated(glyphs[0])


def test_stylistic_set_hides_levels_at_runtime(font_all):
    word = "学生"  # N5
    assert font_all.shape(word, {"ss05": True}) == font_all.plain(word)
    assert font_all.shape(word, {"ss01": True}) == font_all.plain(word)
    hard = "経済"  # N3: hidden by ss03 and ss01, kept by ss05
    assert font_all.annotated(font_all.shape(hard, {"ss05": True})[0])
    assert font_all.shape(hard, {"ss03": True}) == font_all.plain(hard)


def test_calt_off_leaves_text_bare(font_all):
    text = "今日は日本語の勉強をします"
    glyphs = font_all.shape(text, {"calt": False})
    assert len(glyphs) == len(text)
    assert not any(font_all.annotated(g) for g in glyphs)


def test_okurigana_reading_sits_over_the_kanji_only(font_all):
    glyphs = font_all.shape("食べる")
    assert len(glyphs) == 3
    assert font_all.annotated(glyphs[0])  # 食 drawn with た above it
    assert glyphs[1:] == font_all.plain("食べる")[1:]  # べる untouched


def test_ambiguous_lone_kanji_stays_bare(font_all):
    # 食 alone reads た, く or しょく: with no okurigana to tell, no reading.
    assert not font_all.annotated(font_all.shape("食")[0])


def test_vertical_text_is_left_alone(font_all):
    glyphs = font_all.shape("今日", direction="ttb")
    assert not any(font_all.annotated(g) for g in glyphs)


def test_glyph_count_under_the_limit(font_all, font_n5):
    for shaped in (font_all, font_n5):
        count = len(TTFont(shaped.path, lazy=True).getGlyphOrder())
        assert count < MAX_GLYPHS


def test_lone_kanji_with_a_different_suffix_reading_stays_bare(font_all):
    # 都 alone is みやこ, but と as the suffix of 東京都: the font cannot tell.
    assert not font_all.annotated(font_all.shape("都")[0])
