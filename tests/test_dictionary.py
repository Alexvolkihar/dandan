"""Unit tests of the dictionary rules, without downloaded data."""

from __future__ import annotations

from dandan.dictionary import Pair, _choose, _context_starts, split_runs


def test_split_runs_keeps_okurigana_out_of_the_run():
    segments = [{"ruby": "食", "rt": "た"}, {"ruby": "べる"}]
    assert split_runs(segments) == [("食", "た", "べる", (("食", "た"),))]


def test_split_runs_merges_adjacent_kanji_segments():
    segments = [{"ruby": "日本", "rt": "にほん"}, {"ruby": "語", "rt": "ご"}]
    assert split_runs(segments) == [("日本語", "にほんご", "", (("日本", "にほん"), ("語", "ご")))]


def test_split_runs_splits_at_kana():
    segments = [{"ruby": "話", "rt": "はな"}, {"ruby": "し"}, {"ruby": "合", "rt": "あ"}, {"ruby": "う"}]
    runs = split_runs(segments)
    assert [(r[0], r[1], r[2]) for r in runs] == [("話", "はな", "し"), ("合", "あ", "う")]


def test_split_runs_rejects_reading_over_kana():
    assert split_runs([{"ruby": "お巡", "rt": "おまわ"}]) is None


def test_choose_keeps_a_dominant_reading():
    assert _choose({"きょう": (60, 1, 0), "こんにち": (10, 1, 1)}) == "きょう"


def test_choose_drops_close_readings():
    assert _choose({"た": (71, 1, 0), "く": (67, 1, 0)}) is None


def test_context_starts_follow_godan_conjugation():
    pair = Pair(1, "書く", "かく", 0, 50, True, ("v5k",))
    assert set(_context_starts(pair, "く")) == set("かきくけこい")


def test_context_starts_use_the_stable_okurigana():
    pair = Pair(1, "食べる", "たべる", 0, 50, True, ("v1",))
    assert _context_starts(pair, "べる") == ["べ"]
