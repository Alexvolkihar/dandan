# Data sources

Nothing below is committed to this repository. `python -m dandan fetch` downloads every file into `cache/`
(gitignored) and writes `cache/manifest.json` with the URL and SHA-256 of what it got. The built fonts embed
readings derived from the dictionary data, so they carry the attribution and share-alike terms below.

| Data | Used for | Source | Version | License |
| --- | --- | --- | --- | --- |
| Noto Sans JP (variable TrueType) | Base outlines: kanji, kana, Latin, punctuation | [google/fonts `ofl/notosansjp`](https://github.com/google/fonts/tree/main/ofl/notosansjp), `NotoSansJP[wght].ttf` | `main` at download time (2.004) | [SIL OFL 1.1](OFL.txt), Reserved Font Name "Source" |
| JMdict (English) | Written forms, readings, priority tags (`news1`, `ichi1`, `nfXX`...), parts of speech | [EDRDG](https://www.edrdg.org/jmdict/j_jmdict.html), `http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz` | Daily file; SHA-256 recorded in `cache/manifest.json` | [CC BY-SA 4.0](https://www.edrdg.org/edrdg/licence.html), Electronic Dictionary Research and Development Group |
| JmdictFurigana | Which kana go over which kanji (per-kanji reading segmentation) | [Doublevil/JmdictFurigana](https://github.com/Doublevil/JmdictFurigana) release `2.3.1+2026-10-25`, `JmdictFurigana.json.tar.gz` | Pinned release | CC BY-SA 4.0 (same licence as JMdict, per its README) |
| yomitan-jlpt-vocab | JLPT level (N5-N1) of each JMdict entry, form and reading | [stephenmk/yomitan-jlpt-vocab](https://github.com/stephenmk/yomitan-jlpt-vocab) `original_data/n{1..5}.csv` at commit `b062d4e38c4bdd0950ae1d4ec55f04b176182e03` | Pinned commit | [CC BY-SA 4.0](https://github.com/stephenmk/yomitan-jlpt-vocab/blob/main/LICENSE.txt); built on Jonathan Waller's [JLPT lists](http://www.tanos.co.uk/jlpt/) (Creative Commons BY) |

## Notes

- **JLPT lists.** There is no official JLPT vocabulary list since 2010. Waller's lists are a widely used
  estimate (jisho.org uses them too); the level a word gets here is only as good as that estimate. For example
  日本 is listed at N3 and 日本語 is not listed, so both stay annotated in an N5 build.
- **Share-alike.** Any redistributed derivative of the dictionary data (including the compiled
  `cache/dictionary-*.json` or the reading tables inside a built font) stays under CC BY-SA 4.0 with the
  attributions above.
- **Reserved Font Name.** Noto Sans JP reserves the name "Source"; the output family is "Dandan" and never
  uses "Source" or "Noto".
