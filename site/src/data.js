// Facts about the built font (from dist/Dandan.json) and the page's samples.

export const FONT = {
  woff2: 'fonts/Dandan.woff2',
  ttf: 'fonts/Dandan.ttf',
  woff2Bytes: 1888560,
  ttfBytes: 7222332,
  annotated: 57611,
  totalGlyphs: 65471,
  baseGlyphs: 7860,
  candidates: 136639,
}

// The vertical build (dist/Dandan-Vertical.json), loaded only on demand.
export const VERTICAL_FONT = {
  family: 'Dandan Vertical',
  woff2: 'fonts/Dandan-Vertical.woff2',
  ttf: 'fonts/Dandan-Vertical.ttf',
  woff2Bytes: 2053236,
  ttfBytes: 7619188,
}

// Repository URL, shown in the header and footer when set.
export const REPO_URL = ''

// Steps of the level control. `ss` is the stylistic set that hides the
// readings of that level and every easier one.
// Their labels live in src/i18n (levels.none, levels.valueText).
export const LEVELS = [
  { id: 'all', ss: null },
  { id: 'N5', ss: 'ss05' },
  { id: 'N4', ss: 'ss04' },
  { id: 'N3', ss: 'ss03' },
  { id: 'N2', ss: 'ss02' },
  { id: 'N1', ss: 'ss01' },
]

/**
 * The CSS value for a level index (0-5) with furigana on or off. Vertical text
 * has no calt (shapers skip it there), so Dandan Vertical turns readings off
 * with its ss10.
 */
export function featureValue(level, on = true, vertical = false) {
  if (!on) return vertical ? '"ss10" 1' : '"calt" 0'
  const ss = LEVELS[level]?.ss
  return ss ? `"${ss}" 1` : 'normal'
}

// Hero sentences. `step` is the first level index whose stylistic set hides
// the word (1 = N5 ... 5 = N1); 6 = not on any JLPT list, never hidden.
// Checked with HarfBuzz against dist/Dandan.ttf, shaping each kanji run alone
// as browsers do.
export const HERO_LINES = [
  {
    text: '雨の日曜日、図書館で日本語を勉強した。',
    words: [['雨', 1], ['日曜日', 1], ['図書館', 1], ['日本語', 6], ['勉強', 1]],
  },
  {
    text: '経済の状況は複雑だが、政府は対策を検討している。',
    words: [['経済', 2], ['状況', 3], ['複雑', 2], ['政府', 3], ['対策', 4], ['検討', 3]],
  },
  {
    text: '古い友人と再会し、斬新な提案に驚いた。',
    words: [['友人', 3], ['再会', 5], ['斬新', 6], ['提案', 3], ['驚', 2]],
  },
]

export const HERO_WORDS = HERO_LINES.flatMap(line => line.words)

// One word per JLPT level, hidden one by one down the switches table.
export const LADDER = [['勉強', 'N5'], ['経済', 'N4'], ['状況', 'N3'], ['対策', 'N2'], ['再会', 'N1']]

// Playground presets: short texts of growing difficulty, written for this page.
// Their names and hints live in src/i18n (playground.presets).
export const PRESETS = [
  {
    id: 'first-steps',
    text: '私の部屋は小さいですが、窓から公園が見えます。\n週末は友達と映画を見に行く約束をしました。',
  },
  {
    id: 'errands',
    text: '駅の近くに新しい料理屋ができたので、来週の予定を確認した。\n冬の朝、凍えた指で手紙を書いた。',
  },
  {
    id: 'news',
    text: '政府は物価の上昇を抑えるため、新たな経済対策を発表した。\n専門家は、少子化が地域社会に深刻な影響を及ぼすと指摘している。',
  },
  {
    id: 'prose',
    text: '夕暮れの港に汽笛が響き、鴎の群れが静かに旋回していた。\n縁側に座って、祖母は庭の紫陽花を眺めていた。\n段々と寒くなり、山の木々は赤く色づき始めた。',
  },
]

/** A size in MiB with one decimal, in the locale's number format (1.8, 1,8). */
export function mebibytes(bytes, locale = 'en') {
  return new Intl.NumberFormat(locale, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(bytes / 1048576)
}
