"""Command line: python -m dandan {fetch,build,build-all}."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .build import LEVEL_NAMES, build
from .fetch import fetch
from .glyphs import Layout


def _add_build_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--out", type=Path, default=Path("dist"), help="output directory (default: dist)")
    parser.add_argument(
        "--dictionary",
        choices=("full", "common"),
        default="full",
        help="full: JLPT + common words, then other JMdict words up to the glyph budget; "
        "common: only JLPT and priority-tagged JMdict words (smaller font)",
    )
    parser.add_argument("--max-words", type=int, help="cap the number of annotated glyphs")
    parser.add_argument("--weight", type=int, default=400, help="weight of the text (100-900)")
    parser.add_argument("--furigana-weight", type=int, default=600, help="weight of the furigana kana")
    parser.add_argument("--scale", type=float, default=0.5, help="size of the furigana relative to the text")
    parser.add_argument("--no-woff2", action="store_true", help="write the TTF only")


def _run_build(args: argparse.Namespace, level: str, family: str | None) -> None:
    result = build(
        level=level,
        family=family,
        out_dir=args.out,
        max_words=args.max_words,
        include_uncommon=args.dictionary == "full",
        layout=Layout(scale=args.scale),
        weight=args.weight,
        furigana_weight=args.furigana_weight,
        woff2=not args.no_woff2,
    )
    for kind, path in result.files.items():
        print(f"{result.family} [{kind}] {path} ({path.stat().st_size / 1024:.0f} KiB)")
    print(
        f"  glyphs: {result.total_glyphs} = {result.base_glyphs} base + {result.annotated} annotated "
        f"(budget {result.budget}); ascender {result.ascender}, descender {result.descender}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dandan", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("fetch", help="download the base font and the dictionary data")

    one = commands.add_parser("build", help="build one font")
    one.add_argument(
        "--level",
        choices=list(LEVEL_NAMES),
        default="all",
        help="JLPT level the reader knows: its words and the easier ones stay bare (default: all = annotate all)",
    )
    one.add_argument("--family", help='font family name (default: "Dandan" or "Dandan <level>")')
    _add_build_options(one)

    every = commands.add_parser("build-all", help="build the font for every level")
    _add_build_options(every)

    args = parser.parse_args(argv)
    if args.command == "fetch":
        for filename, info in fetch().items():
            print(f"{filename}: {info['sha256'][:16]}  {info['url']}")
    elif args.command == "build":
        _run_build(args, args.level, args.family)
    else:
        for level in LEVEL_NAMES:
            _run_build(args, level, None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
