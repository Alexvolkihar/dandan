// English copy, the reference shape for every locale (see Messages below).
// Strings marked "html" are rendered with v-html: they are static, written here,
// and may only contain <code>, <a> and <wbr> elements.

const en = {
  meta: {
    title: 'Dandan · furigana that fade as you learn',
    description:
      'Dandan is a free Japanese font that draws furigana over kanji with OpenType ligatures, and hides the readings of the JLPT words you already know.',
  },
  skip: 'Skip to content',
  header: {
    brand: 'Dandan, back to top',
    sections: 'Sections',
    playground: 'Playground',
    how: 'How it works',
    use: 'Use it',
    limits: 'Limits',
    source: 'Source',
    download: 'Download',
    toLight: 'Switch to light theme',
    toDark: 'Switch to dark theme',
    language: 'Language',
  },
  common: {
    known: 'I already know',
    furigana: 'Furigana',
    on: 'On',
    off: 'Off',
    copy: 'Copy',
    copyCss: 'Copy CSS',
    copied: 'Copied',
    mb: (size: string) => `${size} MB`,
  },
  levels: {
    none: 'None',
    // aria-valuetext of the staircase, one per step (None, N5 ... N1).
    valueText: [
      'None: every reading shown',
      'N5: readings of N5 words hidden',
      'N4: readings of N5 and N4 words hidden',
      'N3: readings of N5 to N3 words hidden',
      'N2: readings of N5 to N2 words hidden',
      'N1: readings of every word on a JLPT list hidden',
    ],
  },
  hero: {
    eyebrow: 'A free Japanese font · OFL 1.1',
    title: 'Furigana that fade ',
    titleEm: 'as you learn.',
    // html
    lede:
      'Dandan draws readings over kanji by itself: plain text in, furigana out, with no <code>&lt;ruby&gt;</code> and no script. Tell it the JLPT level you know and those words lose their readings, one step at a time.',
    download: 'Download the font',
    try: 'Try your own text',
    specimen: 'Specimen · Dandan Regular',
    loading: (size: string) => `Loading the font (${size})…`,
    loaded: 'Font loaded',
    failed: 'The font did not load: showing a fallback without furigana',
    tally: (n: number) => (n === 1 ? 'word still shows a reading' : 'words still show a reading'),
    statusOff: 'calt is off, so every reading is gone.',
    statusStart: 'Climb the stairs to drop the readings you already know.',
    statusHides: (level: string) => `${level} hides`,
  },
  playground: {
    eyebrow: 'Playground',
    title: 'Type anything. The font does the rest.',
    // html
    intro:
      'The box below is a plain <code>&lt;textarea&gt;</code> set in Dandan. Paste a paragraph, pick the level you read at, and watch which words keep their readings.',
    sample: 'Sample text',
    edited: 'edited',
    presets: {
      'first-steps': { label: 'First steps', hint: 'mostly N5' },
      errands: { label: 'Errands', hint: 'N5 to N3' },
      news: { label: 'News', hint: 'N3 to N1 and beyond' },
      prose: { label: 'Prose', hint: 'literary, many off-list words' },
    },
    size: 'Size',
    lineHeight: 'Line height',
    textLabel: 'Japanese text set in Dandan',
  },
  how: {
    eyebrow: 'How it works',
    title: 'One glyph per word, read and drawn in advance.',
    intro:
      'Every common kanji word, with its reading, is a glyph of its own: the kanji, with the kana at half size above them. OpenType rules pick that glyph when the word appears, and stylistic sets put the plain kanji back for the words you know.',
    flow: 'What happens to 日本語を勉強',
    stages: [
      {
        tag: 'Input',
        title: 'Plain text',
        body: 'Unicode, nothing else. The browser cuts it into runs by script before shaping: 日本語 · を · 勉強.',
      },
      {
        tag: 'calt · words',
        title: 'Longest match',
        body: 'Each run of two or more kanji is a ligature. The longest is tried first, so 日本語 is one glyph, never 日本 + 語.',
      },
      {
        tag: 'ss05 · hide N5',
        title: 'Known words go bare',
        body: '勉強 is an N5 word: after the match, ss05 swaps its glyph back to plain 勉 and 強. 日本語 is not on any list and keeps its reading.',
      },
    ],
    rulesTitle: 'Rules, in order',
    // html
    rules: [
      '<code>words</code> ligatures of two or more kanji, longest first.',
      '<code>okurigana</code> a lone kanji before a given kana takes that word’s reading (食 + べ: た). Browsers shape kanji and kana apart, so only other shapers see this one.',
      '<code>kanji</code> a lone kanji takes its one unambiguous reading (見: み).',
      '<code>hide N5</code> … <code>hide N1</code> turn the glyph of a listed word back into its plain kanji. <code>ss05</code> runs the first, <code>ss01</code> all five.',
    ],
    note: 'A reading is kept only when it clearly wins: lone 食 can be た, く or しょく, so it stays bare. When a reading fits over each kanji it sits there (日 本 語); otherwise it is centred and condensed over the word, so it never spills into the next one.',
    budgetTitle: 'The glyph budget',
    budget: (max: string, candidates: string) =>
      `A font holds at most ${max} glyphs. The dictionary offers ${candidates} words; JLPT words go first, then common JMdict words by frequency, until the font is full.`,
    budgetAria: (base: string, words: string, free: string, max: string) =>
      `${base} base glyphs, ${words} annotated words, ${free} free, out of ${max}`,
    budgetParts: { base: 'Base font', words: 'Annotated words', free: 'Free' },
  },
  use: {
    eyebrow: 'Use it',
    title: 'One font file, seven switches.',
    // html
    intro:
      'Load the WOFF2 like any web font and pick a level with <code>font-feature-settings</code>. The switches work wherever stylistic sets do: CSS, InDesign, Word.',
    caption:
      'Feature switches and what they hide, with 勉強 (N5), 経済 (N4), 状況 (N3), 対策 (N2) and 再会 (N1) rendered in Dandan',
    thSwitch: 'Switch',
    thHides: 'Hides the readings of',
    // One per row: default, ss05 ... ss01, calt 0.
    rows: [
      'Nothing. Every word in the font shows its reading.',
      'N5 words',
      'N5 and N4',
      'N5 to N3',
      'N5 to N2',
      'Every JLPT word; only off-list words keep a reading',
      'Every reading (same as font-variant-ligatures: no-contextual)',
    ],
    // html
    cssNote:
      'The furigana reach 1.34 em above the baseline. Below a line-height of about 1.6 the first line can be clipped by <code>overflow: hidden</code>; below 1.5 the readings touch the line above.',
    buildTitle: 'Build your own',
    terminal: 'Terminal, Python 3.12+',
    // html
    buildNote:
      '<code>--level N4</code> bakes a level into the default <code>calt</code>, for apps that never show stylistic sets; a stylistic set can still raise it, never lower it. Other options: <code>--weight</code>, <code>--furigana-weight</code>, <code>--scale</code>, <code>--max-words</code>.',
    downloadTitle: 'Download',
    web: 'web',
    desktop: 'desktop',
    // html
    downloadNote:
      'Regular weight, every level switchable at run time. Licences: <a href="fonts/OFL.txt">OFL.txt</a> for the font and <a href="fonts/NOTICE.txt">NOTICE.txt</a> for the reading data (CC BY-SA 4.0).',
  },
  limits: {
    eyebrow: 'Limits',
    title: 'What a font cannot know.',
    intro: 'Dandan guesses from the dictionary, without grammar or context. Check readings that matter.',
    items: [
      {
        title: 'Readings can be wrong.',
        body: 'A font sees a run of kanji, not the sentence. The longest match can cut a run in the wrong place, a word with two readings (人気: にんき or ひとけ) always gets its most frequent one, and a rare dictionary compound can grab more text than was meant.',
      },
      {
        title: 'Okurigana are out of reach in browsers.',
        body: 'Browsers shape kanji and kana as separate runs, so the font never sees 食 next to べる. Kanji with several readings, such as 食, 行 and 話, stay bare there.',
      },
      {
        title: 'JLPT levels are an estimate.',
        body: 'There has been no official vocabulary list since 2010. Dandan uses Jonathan Waller’s lists, which put 日本 at N3 and leave 日本語 out, for example.',
      },
      {
        title: 'It is a big file.',
        body: 'About 1.8 MB of WOFF2 for the full dictionary. Build with --dictionary common (about 1.3 MB) or --max-words for less.',
      },
      {
        title: 'A line break can split a word.',
        body: 'When a line wraps inside 提案, each half is shaped alone and may get a reading of its own. word-break: auto-phrase (Chromium, with lang="ja") breaks between phrases instead.',
      },
      {
        title: 'Horizontal, hiragana, JIS X 0208.',
        body: 'Shapers skip calt in vertical writing, so vertical text stays plain. Readings are hiragana only, one weight per build, and words with kanji outside JIS X 0208 (plus 𠮟, 塡, 剝, 頰) get none.',
      },
    ],
  },
  credits: {
    eyebrow: 'Credits',
    title: 'Built on open work.',
    thanks: 'Thanks to',
    // html
    items: [
      '<a href="https://furifont.antfu.me/">Furifont</a> by Anthony Fu, the inspiration: furigana drawn by the font itself, and the finding that browsers shape kanji and kana apart. Dandan is a separate implementation and shares no code with it.',
      '<a href="https://fonts.google.com/noto/specimen/Noto+Sans+JP">Noto Sans JP</a> by Adobe and Google, the outlines.',
      '<a href="https://www.edrdg.org/jmdict/j_jmdict.html">JMdict</a> by the Electronic Dictionary Research and Development Group, the words and readings.',
      '<a href="https://github.com/Doublevil/JmdictFurigana">JmdictFurigana</a> by Doublevil, which kana go over which kanji.',
      '<a href="https://github.com/stephenmk/yomitan-jlpt-vocab">yomitan-jlpt-vocab</a> by stephenmk, from Jonathan Waller’s <a href="http://www.tanos.co.uk/jlpt/">JLPT lists</a>, the levels.',
      '<a href="https://github.com/fonttools/fonttools">fontTools</a> and <a href="https://harfbuzz.github.io/">HarfBuzz</a>, to build and test it.',
    ],
    licences: 'Licences',
    font: 'Font',
    // html
    fontBody:
      '<a href="fonts/OFL.txt">SIL Open Font License 1.1</a>. Derived from Noto Sans JP, © 2014-2021 Adobe, with Reserved Font Name “Source”; the family is named Dandan.',
    data: 'Reading data',
    // html
    dataBody:
      '<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>, from JMdict (EDRDG), JmdictFurigana and yomitan-jlpt-vocab, embedded in the font as reading tables. See <a href="fonts/NOTICE.txt">NOTICE.txt</a>.',
    code: 'Code',
    codeBody: 'MIT, Alexis MABANZA.',
  },
  footer: {
    sign: 'Dandan, step by step. 2026, Alexis MABANZA.',
    setIn: 'Set in Dandan and Instrument Serif.',
    source: 'Source code',
    top: 'Back to top',
  },
}

export type Messages = typeof en

export default en
