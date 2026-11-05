// 日本語の文言。英字と和文の間にスペースは入れない（CSS の text-autospace に任せる）。
// 見出しは word-break: keep-all で組むため、文節の区切りにゼロ幅スペース（\u200b）を入れる。
import type { Messages } from './en'

const ja: Messages = {
  meta: {
    title: 'Dandan（段々）· 覚えるほど消えていくふりがな',
    description:
      'Dandan（段々）は、OpenTypeの合字で漢字の上にふりがなを描く無料の日本語フォントです。習得したJLPTレベルの語は、ふりがなが表示されなくなります。',
  },
  skip: '本文へ移動',
  header: {
    brand: 'Dandan、ページの先頭へ',
    sections: 'セクション',
    playground: '試してみる',
    how: 'しくみ',
    use: '使い方',
    limits: '制限事項',
    source: 'ソース',
    download: 'ダウンロード',
    toLight: 'ライトテーマに切り替え',
    toDark: 'ダークテーマに切り替え',
    language: '言語',
  },
  common: {
    known: '習得済みのレベル',
    furigana: 'ふりがな',
    on: 'オン',
    off: 'オフ',
    copy: 'コピー',
    copyCss: 'CSSをコピー',
    copied: 'コピーしました',
    mb: (size: string) => `${size} MB`,
  },
  levels: {
    none: 'なし',
    valueText: [
      'なし：すべてのふりがなを表示',
      'N5：N5の語のふりがなを非表示',
      'N4：N5〜N4の語のふりがなを非表示',
      'N3：N5〜N3の語のふりがなを非表示',
      'N2：N5〜N2の語のふりがなを非表示',
      'N1：JLPTリストにあるすべての語のふりがなを非表示',
    ],
  },
  hero: {
    eyebrow: '無料の日本語フォント · OFL 1.1',
    title: 'ふりがなは、',
    titleEm: '覚えるほど\u200b消えていく。',
    lede:
      'Dandanは、漢字の上のふりがなを自分で描きます。入力はただのテキストだけ。<code>&lt;ruby&gt;</code>タグもスクリプトも要りません。習得したJLPTレベルを指定すれば、その語のふりがなが一段ずつ消えていきます。',
    download: 'フォントをダウンロード',
    try: '自分の文章で試す',
    specimen: '見本 · Dandan Regular',
    loading: (size: string) => `フォントを読み込んでいます（${size}）…`,
    loaded: 'フォントを読み込みました',
    failed: 'フォントを読み込めませんでした。ふりがなのない代替フォントで表示しています',
    // 数字のあとに続く見出し：「16/16 ふりがなが残っている語」
    tally: () => 'ふりがなが残っている語',
    statusOff: 'caltがオフなので、ふりがなはすべて消えています。',
    statusStart: '階段を上ると、知っている語からふりがなが消えていきます。',
    statusHides: (level: string) => `${level}で消える語：`,
  },
  playground: {
    eyebrow: '試してみる',
    title: '文章を\u200b入れるだけ。あとは\u200bフォントに\u200bおまかせ。',
    intro:
      '下の入力欄は、Dandanで表示しているただの<code>&lt;textarea&gt;</code>です。文章を貼り付けてレベルを選ぶと、どの語にふりがなが残るかがわかります。',
    sample: 'サンプル文',
    edited: '編集済み',
    presets: {
      'first-steps': { label: 'はじめの一歩', hint: 'ほぼN5' },
      errands: { label: '日々の用事', hint: 'N5〜N3' },
      news: { label: 'ニュース', hint: 'N3〜N1以上' },
      prose: { label: '文学', hint: '文芸調。リスト外の語が多め' },
    },
    size: '文字サイズ',
    lineHeight: '行の高さ',
    textLabel: 'Dandanで表示した日本語テキスト',
  },
  how: {
    eyebrow: 'しくみ',
    title: '一語に\u200bひとつの\u200bグリフ。読みは\u200b最初から\u200b描いてあります。',
    intro:
      'よく使われる漢字の語は、読みも含めてそれぞれ一つのグリフになっています。漢字の上に、半分の大きさのかなを載せたものです。語が現れるとOpenTypeのルールがそのグリフを選び、知っている語はスタイリスティックセットがふりがなのない漢字に戻します。',
    flow: '「日本語を勉強」が表示されるまで',
    stages: [
      {
        tag: '入力',
        title: 'ただの\u200bテキスト',
        body: 'Unicodeの文字列だけです。ブラウザはシェーピングの前に、文字の種類ごとにテキストを区切ります（日本語 · を · 勉強）。',
      },
      {
        tag: 'calt · words',
        title: '最長一致',
        body: '二文字以上続く漢字は、それぞれが一つの合字です。長いものから順に試すので、日本語は日本＋語ではなく、必ず一つのグリフになります。',
      },
      {
        tag: 'ss05 · hide N5',
        title: '知っている語は\u200bふりがななし',
        body: '勉強はN5の語です。一致したあと、ss05がそのグリフをふりがなのない「勉」と「強」に戻します。日本語はどのリストにもないので、ふりがなが残ります。',
      },
    ],
    rulesTitle: '処理の順番',
    rules: [
      '<code>words</code> 二文字以上の漢字の合字。長いものを優先します。',
      '<code>okurigana</code> 特定のかなが後に続く一字の漢字に、その語の読みを付けます（食＋べ：た）。ブラウザは漢字とかなを別々にシェーピングするため、このルールが働くのはほかのシェーピングエンジンだけです。',
      '<code>kanji</code> 読みが一つに決まる一字の漢字に、その読みを付けます（見：み）。',
      '<code>hide N5</code>〜<code>hide N1</code> リストにある語のグリフを、ふりがなのない漢字に戻します。<code>ss05</code>は最初の一つだけ、<code>ss01</code>は五つすべてを適用します。',
    ],
    note: '読みを付けるのは、その読みがはっきり優勢な場合だけです。一字の「食」は「た」「く」「しょく」と読めるため、ふりがなは付きません。読みを一字ずつ割り振れる場合はそれぞれの漢字の上に（日 本 語）、そうでない場合は語の中央に詰めて載せるので、隣の語にはみ出すことはありません。',
    budgetTitle: 'グリフ数の上限',
    budget: (max: string, candidates: string) =>
      `一つのフォントに入るグリフは最大${max}個です。辞書には${candidates}語ありますが、JLPTの語を優先し、続いてJMdictのよく使われる語を頻度順に、フォントがいっぱいになるまで収録しています。`,
    budgetAria: (base: string, words: string, free: string, max: string) =>
      `基本グリフ${base}個、ふりがな付きの語${words}個、空き${free}個（上限${max}個）`,
    budgetParts: { base: '基本フォント', words: 'ふりがな付きの語', free: '空き' },
  },
  use: {
    eyebrow: '使い方',
    title: 'フォントファイルは\u200b一つ、スイッチは\u200b七つ。',
    intro:
      'WOFF2を通常のWebフォントと同じように読み込み、<code>font-feature-settings</code>でレベルを選びます。スタイリスティックセットが使える環境なら、CSSでもInDesignでもWordでも使えます。',
    caption:
      '各スイッチと、ふりがなが消える語。勉強（N5）、経済（N4）、状況（N3）、対策（N2）、再会（N1）をDandanで表示',
    thSwitch: 'スイッチ',
    thHides: 'ふりがなが消える語',
    rows: [
      'なし。フォントに収録されたすべての語にふりがなが付きます。',
      'N5の語',
      'N5〜N4の語',
      'N5〜N3の語',
      'N5〜N2の語',
      'JLPTのすべての語。リスト外の語だけにふりがなが残ります',
      'すべて（font-variant-ligatures: no-contextual と同じ）',
    ],
    cssNote:
      'ふりがなはベースラインから1.34emの高さまで届きます。行の高さが1.6程度より小さいと<code>overflow: hidden</code>で1行目が欠けることがあり、1.5より小さいと上の行にふりがなが接してしまいます。',
    buildTitle: '自分で\u200bビルドする',
    terminal: 'ターミナル（Python 3.12以上）',
    buildNote:
      '<code>--level N4</code>を付けると、そのレベルが既定の<code>calt</code>に組み込まれます。スタイリスティックセットを選べないアプリ向けです。スタイリスティックセットでレベルを上げることはできますが、下げることはできません。そのほかのオプション：<wbr><code>--weight</code>、<wbr><code>--furigana-weight</code>、<wbr><code>--scale</code>、<wbr><code>--max-words</code>',
    downloadTitle: 'ダウンロード',
    web: 'Web用',
    desktop: 'デスクトップ用',
    downloadNote:
      'ウェイトはRegularのみで、どのレベルも表示時に切り替えられます。ライセンスは、フォントが<a href="fonts/OFL.txt">OFL.txt</a>、読みのデータが<a href="fonts/NOTICE.txt">NOTICE.txt</a>（CC BY-SA 4.0）です。',
  },
  limits: {
    eyebrow: '制限事項',
    title: 'フォントには\u200bわからないこと。',
    intro: 'Dandanは、文法も文脈も見ずに辞書だけで読みを推測します。大切な読みは必ず確認してください。',
    items: [
      {
        title: '読みが\u200b間違っていることが\u200bあります。',
        body: 'フォントに見えるのは漢字の並びだけで、文全体ではありません。最長一致で区切る位置を誤ることがあり、読みが二つある語（人気：にんき／ひとけ）には、いつも頻度の高いほうが付きます。辞書にあるまれな複合語が、意図より長い範囲を取ってしまうこともあります。',
      },
      {
        title: 'ブラウザでは\u200b送りがなを\u200b考慮できません。',
        body: 'ブラウザは漢字とかなを別々のまとまりとしてシェーピングするため、フォントからは「食」と「べる」が並んでいることがわかりません。食・行・話のように読みが複数ある漢字は、ブラウザではふりがななしになります。',
      },
      {
        title: 'JLPTレベルは\u200b目安です。',
        body: '2010年以降、公式の語彙リストはありません。DandanはJonathan Waller氏のリストを使っています。このリストでは、たとえば「日本」はN3で、「日本語」は含まれていません。',
      },
      {
        title: 'ファイルサイズが\u200b大きめです。',
        body: '辞書をすべて収録したWOFF2は約1.8 MBです。--dictionary common（約1.3 MB）や--max-wordsを指定してビルドすれば、小さくできます。',
      },
      {
        title: '改行で\u200b語が\u200b分かれることが\u200bあります。',
        body: '「提案」の途中で改行されると、前後がそれぞれ単独でシェーピングされ、別の読みが付くことがあります。word-break: auto-phrase（Chromium、lang="ja"指定時）を使えば、文節の切れ目で改行されます。',
      },
      {
        title: '横書き、ひらがな、JIS X 0208。',
        body: '縦書きではシェーピングエンジンがcaltを適用しないため、ふりがなは付きません。読みはひらがなのみ、ウェイトはビルドごとに一つです。JIS\u00a0X\u00a00208にない漢字（および𠮟・塡・剝・頰）を含む語には、ふりがなが付きません。',
      },
    ],
  },
  credits: {
    eyebrow: 'クレジット',
    title: 'オープンな成果に\u200b支えられて。',
    thanks: '謝辞',
    items: [
      'Anthony Fu氏の<a href="https://furifont.antfu.me/">Furifont</a>。フォント自身がふりがなを描くというアイデアと、ブラウザが漢字とかなを別々にシェーピングするという発見は、ここから着想を得ました。Dandanは独立した実装で、コードは共有していません。',
      'グリフの輪郭は、AdobeとGoogleの<a href="https://fonts.google.com/noto/specimen/Noto+Sans+JP">Noto Sans JP</a>。',
      '語と読みは、Electronic Dictionary Research and Development Groupの<a href="https://www.edrdg.org/jmdict/j_jmdict.html">JMdict</a>。',
      'どのかなをどの漢字の上に載せるかは、Doublevil氏の<a href="https://github.com/Doublevil/JmdictFurigana">JmdictFurigana</a>。',
      'レベルは、Jonathan Waller氏の<a href="http://www.tanos.co.uk/jlpt/">JLPTリスト</a>をもとにした、stephenmk氏の<a href="https://github.com/stephenmk/yomitan-jlpt-vocab">yomitan-jlpt-vocab</a>。',
      'ビルドとテストには、<a href="https://github.com/fonttools/fonttools">fontTools</a>と<a href="https://harfbuzz.github.io/">HarfBuzz</a>。',
    ],
    licences: 'ライセンス',
    font: 'フォント',
    fontBody:
      '<a href="fonts/OFL.txt">SIL Open Font License 1.1</a>。Noto Sans JP（© 2014-2021 Adobe、予約フォント名「Source」）から派生したため、ファミリー名はDandanとしています。',
    data: '読みのデータ',
    dataBody:
      '<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>。JMdict（EDRDG）、JmdictFurigana、yomitan-jlpt-vocabに由来し、読みのテーブルとしてフォントに組み込まれています。詳しくは<a href="fonts/NOTICE.txt">NOTICE.txt</a>をご覧ください。',
    code: 'コード',
    codeBody: 'MIT、Alexis MABANZA',
  },
  footer: {
    sign: 'Dandan、一段ずつ。2026年 Alexis MABANZA',
    setIn: 'DandanとInstrument Serifで組んでいます。',
    source: 'ソースコード',
    top: 'ページの先頭へ',
  },
}

export default ja
