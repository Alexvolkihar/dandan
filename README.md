# Dandan 段々

[![CI](https://github.com/Alexvolkihar/dandan/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/Alexvolkihar/dandan/actions/workflows/ci.yml)

A Japanese font that draws furigana over kanji by itself, and drops the readings of the JLPT words you
already know.

[![The Dandan landing page: the JLPT staircase hides readings level by level, the furigana switch turns them all off, then Japanese is typed into the playground](docs/images/demo.gif)](docs/images/demo.mp4)

<sub>24-second demo of the website, also as [MP4](docs/images/demo.mp4).</sub>

**Live site: [dandan.alexvolkihar.ovh](https://dandan.alexvolkihar.ovh)** (specimen, playground, download)

## What it does

Dandan is built on Noto Sans JP. Its OpenType ligatures replace each kanji word with a glyph that carries its
reading above it, so plain text gets furigana with no `<ruby>` markup and no JavaScript. About 57,600 words are
annotated, JLPT vocabulary first.

Stylistic sets tell the font what the reader already knows. Each one hides the readings of a JLPT level and
every easier level, while harder words keep theirs. The name 段々 (*dandan*) means "step by step".

| `font-feature-settings` | The reader knows | Readings hidden |
| --- | --- | --- |
| `normal` | nothing yet | none |
| `"ss05" 1` | N5 | N5 words |
| `"ss04" 1` | N5 and N4 | N5 to N4 |
| `"ss03" 1` | N5 to N3 | N5 to N3 |
| `"ss02" 1` | N5 to N2 | N5 to N2 |
| `"ss01" 1` | every level | every word on a JLPT list (off-list words keep their reading) |
| `"calt" 0` | | all of them: no furigana at all (same as `font-variant-ligatures: no-contextual`) |

![The same three sentences in Dandan at three levels: all 16 words annotated by default, 9 with ss04, 2 with ss01](docs/images/levels.png)

One font file switches levels at run time. Apps that expose stylistic sets (CSS, InDesign, Word) can use the
switches; for apps that only apply default features, a level can be baked in at build time (see below).

## Quick start

```css
@font-face {
  font-family: "Dandan";
  src: url("Dandan.woff2") format("woff2");
  font-display: swap;
}

.jp {
  font-family: "Dandan", sans-serif;
  line-height: 1.8;         /* furigana need 1.7 or more */
  word-break: auto-phrase;  /* wrap between words (Chromium, with lang="ja") */
}

.knows-n4 { font-feature-settings: "ss04" 1; }  /* hide N5 and N4 readings */
.plain    { font-feature-settings: "calt" 0; }  /* no furigana */
```

```html
<p lang="ja" class="jp knows-n4">経済の状況は複雑だが、政府は対策を検討している。</p>
```

Keep `line-height` at 1.7 or more. The furigana reach 1.34 em above the baseline and the font's ascender is
raised to 1.36 em, so `line-height: normal` comes out at about 1.65. Below about 1.6 a container with
`overflow: hidden` can clip the first line's furigana, and below about 1.5 they touch the line above.

`word-break: auto-phrase` matters because a line break inside a word splits it into two runs, and each half
may then get a reading of its own.

## Download

- From the website: [dandan.alexvolkihar.ovh](https://dandan.alexvolkihar.ovh), WOFF2 (1.8 MB) or TTF (6.9 MB).
- From this repository: [`site/public/fonts/`](site/public/fonts) holds `Dandan.woff2`, `Dandan.ttf`, the
  OFL and the attribution notice. Keep `OFL.txt` and `NOTICE.txt` next to the font when you redistribute it.

These files are the `all` build (every reading shown by default, levels picked with stylistic sets). Fonts
with a level baked in come from a build.

## Build from source

Python 3.12 or later.

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m dandan fetch                       # base font + dictionaries into cache/ (about 60 MB)
.venv/bin/python -m dandan build                       # dist/Dandan.ttf, .woff2, .json
.venv/bin/python -m dandan build --level N4 --family "Dandan N4"
.venv/bin/python -m dandan build-all                   # all, N5, N4, N3, N2, N1 into dist/
```

`build` writes `dist/<Family>.ttf`, `dist/<Family>.woff2` and `dist/<Family>.json` (glyph counts, budget,
features). `fetch` records the URL and SHA-256 of every download in `cache/manifest.json`.

| Option | Default | |
| --- | --- | --- |
| `--level N5\|N4\|N3\|N2\|N1\|all` | `all` | Level already known: its words and the easier ones are bare by default (`build` only) |
| `--family NAME` | `Dandan` / `Dandan <level>` | Family name; never "Source" or "Noto" (see Licences) |
| `--dictionary full\|common` | `full` | `common`: JLPT and JMdict priority words only (23,098 glyphs, WOFF2 about 1.3 MB) |
| `--max-words N` | glyph budget | Cap the number of annotated glyphs |
| `--weight`, `--furigana-weight` | 400, 600 | Weight of the text and of the furigana kana |
| `--scale` | 0.5 | Furigana size relative to the text |
| `--out DIR` | `dist` | Output directory |
| `--no-woff2` | | TTF only |

A baked-in level can be raised further with a stylistic set, never lowered: `--level N4` with `"ss02" 1` hides
N5 to N2. The first build prepares the subset base font and compiles the dictionary into `cache/`; later
builds take about a minute each.

Every level build has the same 65,471 glyphs and the same size (1,888,560 bytes of WOFF2 for `all`, within a
few hundred bytes for the others; 6.9 MB of TTF). A known word still needs its ligature to win the longest
match, so only the rules differ.

`demo/index.html` is a bare test page for the built font: serve the repository root with
`python3 -m http.server 8000` and open `http://localhost:8000/demo/`.

## How it works

![What happens to 日本語を勉強: plain text, then the calt word ligatures add readings, then ss05 makes the N5 word 勉強 bare again](docs/images/how-it-works.png)

```
JMdict ─┬─ (form, reading) pairs, priority tags, parts of speech
        │
JmdictFurigana ── which kana go over which kanji ──┐
                                                   ├─▶ Han runs + readings + JLPT level ─▶ annotated glyphs
JLPT lists (yomitan-jlpt-vocab) ── level per word ─┘                                      + GSUB lookups
Noto Sans JP (variable) ─▶ subset to JIS X 0208 + kana + Latin ─▶ instanced at 400 (text) and 600 (furigana)
```

1. **Han runs.** Browsers split text by script before shaping, so the font sees 食 and べる in separate runs.
   Every dictionary word is cut into maximal runs of kanji, each with its aligned reading
   (`dandan/dictionary.py`).
2. **One reading or none.** A run keeps a reading only when common words clearly agree on it. Inside one JMdict
   entry the first listed reading wins (今日 is きょう, not こんにち); across entries a reading must weigh at least
   three times the next one. Otherwise the run stays bare: 2,166 runs end up bare this way, lone 食 (た, く,
   しょく) among them. A lone kanji also stays bare when a common affix or counter reads it differently (都 is
   みやこ alone but と in 東京都).
3. **Glyphs.** Each kept (run, reading) pair becomes one TrueType composite glyph: the base kanji side by side,
   with the kana at half size above them, taken from a weight-600 instance so the small kana keep their colour.
   A reading sits over its own kanji when it fits (日[に]本[ほん]語[ご]); otherwise it is centred over the word
   and condensed to its width (`dandan/glyphs.py`).
4. **Rules** (`dandan/gsub.py`), appended to the base font's GSUB in this order:
   - `words`: ligatures of two or more kanji, longest first, so 日本語 beats 日本;
   - `okurigana`: a lone kanji followed by a given kana takes that word's reading (食 + べ: た);
   - `kanji`: a lone kanji takes its one unambiguous reading (見る: み);
   - `hide N5` to `hide N1`: turn the annotated glyph of a listed word back into its plain kanji. They run after
     the ligatures, so a known word still wins the longest match and its kanji are never annotated one by one.
5. **Glyph budget.** OpenType allows 65,535 glyphs. The subset base font keeps 7,860 (JIS X 0208 with its 6,355
   level 1 and 2 kanji, kana, Latin, punctuation and the furigana kana); with 64 ids in reserve, 57,611 remain
   for words. The full dictionary offers 136,639 candidates, taken in this order: JLPT words, JMdict priority
   words by frequency, then other JMdict words (level 1 kanji and shorter words first).
6. **Metrics.** The ascender (hhea, typo, win) is raised from 1160 to 1360 units, just above the furigana.

The [How it works](https://dandan.alexvolkihar.ovh/#how) section of the website walks through the same steps.
[DATA_SOURCES.md](DATA_SOURCES.md) lists every input with its version and licence.

## Limitations

- **Readings can be wrong.** A font sees a run of kanji, not the sentence. The longest match can cut a run in
  the wrong place, a word with two readings (人気: にんき or ひとけ) always gets its most frequent one, and a
  rare JMdict compound can grab more text than the writer meant. Check readings that matter.
- **Okurigana rules don't apply in browsers.** Browsers shape kanji and kana as separate runs, so the font never
  sees 食 next to べ. Only the lone-kanji rule applies there, and kanji with several readings (食, 行, 話) stay
  bare. HarfBuzz given a whole string does apply them. Irregular verbs are skipped.
- **JLPT levels are an estimate.** There has been no official vocabulary list since 2010. Waller's lists put
  日本 at N3 and leave 日本語 out, for example, so 日本語 keeps its reading even with `ss01`.
- **Size.** About 1.8 MB of WOFF2 for the full dictionary. `--dictionary common` (about 1.3 MB) or
  `--max-words` give a smaller file.
- **Horizontal text only.** Shapers skip `calt` in vertical writing (`writing-mode: vertical-rl`), so vertical
  text stays plain.
- **Coverage.** Kanji outside JIS X 0208 (plus 𠮟, 塡, 剝, 頰) are not in the font, and words using them get
  no reading. Furigana are hiragana only, and each build has one weight.

## Website

[`site/`](site) is the landing page at [dandan.alexvolkihar.ovh](https://dandan.alexvolkihar.ovh): a static
Vue 3 + Vite site with the level staircase, a playground, the switches and the downloads. It follows the
system theme and has a light/dark toggle.

<p>
  <img src="docs/images/hero-light.png" alt="Website hero in the light theme: title, three annotated sentences, the JLPT staircase and the furigana switch" width="49%">
  <img src="docs/images/hero-dark.png" alt="The same hero in the dark theme" width="49%">
</p>

![The playground: the News sample at level N4, where easy words are bare and harder ones keep their readings, with the matching CSS below](docs/images/playground.png)

```sh
cd site
pnpm install
pnpm fonts   # copy ../dist/Dandan.woff2, Dandan.ttf and ../OFL.txt into public/fonts (build the font first)
pnpm dev     # local dev server
pnpm build   # static output in site/dist
```

[site/DEPLOY.md](site/DEPLOY.md) covers hosting on GitHub Pages or Cloudflare Pages.

## Tests

```sh
.venv/bin/python -m pytest
```

The 20 tests check the dictionary compiler and run HarfBuzz (uharfbuzz) on the fonts in `dist/`, building them
into a temporary directory when needed: 今日 is one annotated ligature, 日本語 beats 日本, an N5 word is bare in
the N5 build and annotated in `all`, `ss05` and `ss03` hide levels at run time, `calt` off leaves text bare,
okurigana readings sit over the kanji only, vertical text is left alone, and the glyph count stays under
65,535.

`scripts/render.py docs/sample.html docs/sample.png 1000x620` renders [a sample page](docs/sample.png) with
headless Chrome, to check what a browser draws.

## CI and deployment

[`ci.yml`](.github/workflows/ci.yml) runs on every push to `master` and every pull request, in two jobs:

- `site`: `pnpm install --frozen-lockfile` and `pnpm build` in `site/` (pnpm 11, Node 22);
- `python`: on Python 3.12 and 3.14, `python -m dandan fetch` then `python -m pytest -v`, which builds the
  two fonts the shaping tests need. The downloaded sources are cached under a key that follows the pins in
  `dandan/fetch.py`, so a new pin downloads everything again.

Vercel deploys the site on its own: every push to `master` goes live at
[dandan.alexvolkihar.ovh](https://dandan.alexvolkihar.ovh), and every pull request gets a preview URL. The
Vercel project builds `site/` with `pnpm build`; the CI run is a separate check on the same commit.

[`release.yml`](.github/workflows/release.yml) runs on a `v*` tag (`git tag v0.2.0 && git push origin v0.2.0`):
it builds every level with `build-all`, runs the tests on those fonts, and attaches the WOFF2 and TTF files,
`OFL.txt` and `NOTICE.txt` to a GitHub Release.

## Credits

- [Furifont](https://github.com/antfu/furifont) by Anthony Fu showed that a font can set its own furigana, and
  that browsers shape kanji and kana in separate runs. Dandan is a separate implementation in Python with
  fontTools and shares no code with it.
- [Noto Sans JP](https://fonts.google.com/noto/specimen/Noto+Sans+JP) by Adobe and Google, for every outline.
- [JMdict](https://www.edrdg.org/jmdict/j_jmdict.html) by the Electronic Dictionary Research and Development
  Group (EDRDG), for words, readings and frequency tags.
- [JmdictFurigana](https://github.com/Doublevil/JmdictFurigana) by Doublevil, for which kana go over which kanji.
- [yomitan-jlpt-vocab](https://github.com/stephenmk/yomitan-jlpt-vocab) by stephenmk, built on Jonathan
  Waller's [JLPT lists](http://www.tanos.co.uk/jlpt/), for the levels.
- [fontTools](https://github.com/fonttools/fonttools) and [HarfBuzz](https://harfbuzz.github.io/).

## Licences

| What | Licence |
| --- | --- |
| Code (`dandan/`, `scripts/`, `site/`, tests) | [MIT](LICENSE), Alexis MABANZA |
| Fonts (outlines, furigana glyphs, OpenType rules) | [SIL Open Font License 1.1](OFL.txt). Derived from Noto Sans JP, Copyright 2014-2021 Adobe, Reserved Font Name "Source"; the family name "Dandan" uses neither "Source" nor "Noto". |
| Reading data inside the fonts | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), from JMdict (EDRDG), JmdictFurigana and yomitan-jlpt-vocab (Waller's lists are CC BY) |

The dictionary files themselves are not committed; `dandan fetch` downloads them. Anyone redistributing a
modified font or the reading data keeps these attributions and the share-alike terms. The full notice is in
[`site/public/fonts/NOTICE.txt`](site/public/fonts/NOTICE.txt), and sources, versions and checksums are in
[DATA_SOURCES.md](DATA_SOURCES.md).
