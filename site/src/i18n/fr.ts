// Copie française. Écrire une espace ordinaire avant : ; ! ? et à l’intérieur
// des « » : frenchSpacing() la remplace par l’espace insécable qui convient.
import type { Messages } from './en'

const fr: Messages = {
  meta: {
    title: 'Dandan · des furigana qui s’effacent au fil de vos progrès',
    description:
      'Dandan est une police japonaise gratuite qui dessine les furigana au-dessus des kanji grâce aux ligatures OpenType, et masque la lecture des mots JLPT que vous connaissez déjà.',
  },
  skip: 'Aller au contenu',
  header: {
    brand: 'Dandan, retour en haut de page',
    sections: 'Sections',
    playground: 'Atelier',
    how: 'Fonctionnement',
    use: 'Utilisation',
    limits: 'Limites',
    source: 'Source',
    download: 'Télécharger',
    toLight: 'Passer au thème clair',
    toDark: 'Passer au thème sombre',
    language: 'Langue',
  },
  common: {
    known: 'Je connais déjà',
    furigana: 'Furigana',
    on: 'Oui',
    off: 'Non',
    copy: 'Copier',
    copyCss: 'Copier le CSS',
    copied: 'Copié',
    mb: (size: string) => `${size} Mo`,
  },
  levels: {
    none: 'Aucun',
    valueText: [
      'Aucun : toutes les lectures sont affichées',
      'N5 : lectures des mots N5 masquées',
      'N4 : lectures des mots N5 et N4 masquées',
      'N3 : lectures des mots N5 à N3 masquées',
      'N2 : lectures des mots N5 à N2 masquées',
      'N1 : lectures de tous les mots des listes JLPT masquées',
    ],
  },
  hero: {
    eyebrow: 'Une police japonaise libre · OFL 1.1',
    title: 'Des furigana qui s’effacent ',
    titleEm: 'au fil de vos progrès.',
    lede:
      'Dandan place lui-même les lectures au-dessus des kanji : du texte brut en entrée, des furigana en sortie, sans <code>&lt;ruby&gt;</code> ni script. Indiquez le niveau JLPT que vous maîtrisez et ces mots perdent leur lecture, marche après marche.',
    download: 'Télécharger la police',
    try: 'Essayer avec votre texte',
    specimen: 'Spécimen · Dandan Regular',
    loading: (size: string) => `Chargement de la police (${size})…`,
    loaded: 'Police chargée',
    failed: 'La police n’a pas pu être chargée : affichage de secours, sans furigana',
    // En français, 0 et 1 prennent le singulier.
    tally: (n: number) => (n <= 1 ? 'mot affiche encore sa lecture' : 'mots affichent encore leur lecture'),
    statusOff: 'calt est désactivé : plus aucune lecture n’est affichée.',
    statusStart: 'Montez les marches pour retirer les lectures que vous connaissez déjà.',
    statusHides: (level: string) => `${level} masque :`,
  },
  playground: {
    eyebrow: 'Atelier',
    title: 'Tapez ce que vous voulez. La police fait le reste.',
    intro:
      'Le champ ci-dessous est un simple <code>&lt;textarea&gt;</code> composé en Dandan. Collez un paragraphe, choisissez votre niveau et regardez quels mots gardent leur lecture.',
    sample: 'Texte d’exemple',
    edited: 'modifié',
    presets: {
      'first-steps': { label: 'Premiers pas', hint: 'surtout du N5' },
      errands: { label: 'Au quotidien', hint: 'du N5 au N3' },
      news: { label: 'Actualité', hint: 'du N3 au N1, et au-delà' },
      prose: { label: 'Prose', hint: 'littéraire, beaucoup de mots hors liste' },
    },
    size: 'Taille',
    lineHeight: 'Interligne',
    textLabel: 'Texte japonais composé en Dandan',
    direction: 'Sens',
    horizontal: 'Horizontal',
    vertical: 'Vertical',
    verticalLoading: (size: string) => `Chargement de Dandan Vertical (${size})…`,
    verticalFailed: 'Dandan Vertical ne s’est pas chargée : le texte s’affiche sans furigana.',
  },
  how: {
    eyebrow: 'Fonctionnement',
    title: 'Un glyphe par mot, lu et dessiné d’avance.',
    intro:
      'Chaque mot courant écrit en kanji a son propre glyphe, lecture comprise : les kanji, surmontés de leurs kana en demi-taille. Les règles OpenType choisissent ce glyphe quand le mot apparaît, et les jeux stylistiques rendent leurs kanji nus aux mots que vous connaissez.',
    flow: 'Ce que devient 日本語を勉強',
    stages: [
      {
        tag: 'Entrée',
        title: 'Du texte brut',
        body: 'De l’Unicode, rien de plus. Avant la mise en forme, le navigateur découpe le texte en segments selon l’écriture : 日本語 · を · 勉強.',
      },
      {
        tag: 'calt · words',
        title: 'La plus longue correspondance',
        body: 'Chaque suite d’au moins deux kanji est une ligature. La plus longue est essayée d’abord : 日本語 forme donc un seul glyphe, jamais 日本 + 語.',
      },
      {
        tag: 'ss05 · hide N5',
        title: 'Les mots connus restent nus',
        body: '勉強 est un mot N5 : une fois la correspondance trouvée, ss05 remplace son glyphe par les simples 勉 et 強. 日本語 ne figure sur aucune liste et garde sa lecture.',
      },
    ],
    rulesTitle: 'Les règles, dans l’ordre',
    rules: [
      '<code>words</code> ligatures d’au moins deux kanji, la plus longue d’abord.',
      '<code>okurigana</code> un kanji isolé suivi d’un kana donné prend la lecture de ce mot (食 + べ : た). Les navigateurs mettent en forme kanji et kana séparément : seuls les autres moteurs de rendu voient cette règle.',
      '<code>kanji</code> un kanji isolé prend son unique lecture, quand elle est sans ambiguïté (見 : み).',
      '<code>hide N5</code> … <code>hide N1</code> rendent au glyphe d’un mot listé ses kanji nus. <code>ss05</code> applique la première, <code>ss01</code> les cinq.',
    ],
    note: 'Une lecture n’est retenue que si elle s’impose nettement : 食 seul peut se lire た, く ou しょく, il reste donc nu. Quand la lecture se répartit sur chaque kanji, elle s’y place (日 本 語) ; sinon, elle est centrée et resserrée au-dessus du mot, sans jamais déborder sur le suivant.',
    budgetTitle: 'Le budget de glyphes',
    budget: (max: string, candidates: string) =>
      `Une police contient au plus ${max} glyphes. Le dictionnaire propose ${candidates} mots : les mots JLPT passent d’abord, puis les mots courants de JMdict par fréquence, jusqu’à ce que la police soit pleine.`,
    budgetAria: (base: string, words: string, free: string, max: string) =>
      `${base} glyphes de base, ${words} mots annotés, ${free} libres, sur ${max}`,
    budgetParts: { base: 'Police de base', words: 'Mots annotés', free: 'Libres' },
  },
  use: {
    eyebrow: 'Utilisation',
    title: 'Un seul fichier, sept réglages.',
    intro:
      'Chargez le WOFF2 comme n’importe quelle police web et choisissez un niveau avec <code>font-feature-settings</code>. Ces réglages fonctionnent partout où les jeux stylistiques sont pris en charge : CSS, InDesign, Word.',
    caption:
      'Les réglages et les lectures qu’ils masquent, avec 勉強 (N5), 経済 (N4), 状況 (N3), 対策 (N2) et 再会 (N1) composés en Dandan',
    thSwitch: 'Réglage',
    thHides: 'Lectures masquées',
    rows: [
      'Aucune. Chaque mot de la police affiche sa lecture.',
      'Mots N5',
      'Mots N5 et N4',
      'Mots N5 à N3',
      'Mots N5 à N2',
      'Tous les mots JLPT ; seuls les mots hors liste gardent une lecture',
      'Toutes (comme font-variant-ligatures: no-contextual)',
    ],
    cssNote:
      'Les furigana montent jusqu’à 1,34 em au-dessus de la ligne de base. Sous un interligne d’environ 1,6, <code>overflow: hidden</code> peut rogner la première ligne ; sous 1,5, les lectures touchent la ligne du dessus.',
    buildTitle: 'Compiler la vôtre',
    terminal: 'Terminal, Python 3.12 ou plus',
    buildNote:
      '<code>--level N4</code> intègre un niveau au <code>calt</code> par défaut, pour les applications qui ne proposent pas les jeux stylistiques ; un jeu stylistique peut encore relever ce niveau, jamais l’abaisser. Autres options : <code>--weight</code>, <code>--furigana-weight</code>, <code>--scale</code>, <code>--max-words</code>.',
    verticalTitle: 'Texte vertical',
    // html
    verticalNote:
      'Pour <code>writing-mode: vertical-rl</code>, prenez Dandan Vertical : les lectures se placent à droite de chaque kanji, debout, comme dans le tategaki imprimé. Son <code>line-height: normal</code> vaut 2,0, et les furigana demandent 2,0 ou plus. Les jeux stylistiques sont les mêmes ; <code>calt</code> ne s’applique pas en vertical, c’est donc <code>"ss10" 1</code> qui retire toutes les lectures.',
    duoTitle: 'Les deux sens',
    // html
    duoNote:
      'Dandan Duo réunit les règles des deux polices : lectures au-dessus des kanji en texte horizontal, à leur droite en texte vertical, selon le seul <code>writing-mode</code>. Les jeux stylistiques marchent dans les deux sens ; pour retirer toutes les lectures, combinez <code>"calt" 0</code> (horizontal) et <code>"ss10" 1</code> (vertical). Les deux jeux de glyphes se partagent la limite de glyphes d’une police : elle annote donc 28 705 mots par sens au lieu de 57 611, soit tous les mots JLPT et tous les mots courants de JMdict, mais moins de mots rares. Gardez un interligne de 2,0 ou plus en vertical : son <code>line-height: normal</code> est celui de Dandan, 1,65.',
    downloadTitle: 'Télécharger',
    web: 'web',
    desktop: 'bureau',
    vertical: 'vertical',
    both: 'deux sens',
    downloadNote:
      'Graisse Regular, chaque niveau activable à l’usage. Licences : <a href="fonts/OFL.txt">OFL.txt</a> pour la police et <a href="fonts/NOTICE.txt">NOTICE.txt</a> pour les données de lecture (CC BY-SA 4.0).',
  },
  limits: {
    eyebrow: 'Limites',
    title: 'Ce qu’une police ne peut pas savoir.',
    intro: 'Dandan devine à partir du dictionnaire, sans grammaire ni contexte. Vérifiez les lectures qui comptent.',
    items: [
      {
        title: 'Une lecture peut être fausse.',
        body: 'Une police voit une suite de kanji, pas la phrase. La plus longue correspondance peut couper cette suite au mauvais endroit, un mot à deux lectures (人気 : にんき ou ひとけ) reçoit toujours la plus fréquente, et un composé rare du dictionnaire peut englober plus de texte que prévu.',
      },
      {
        title: 'Les okurigana sont hors de portée dans les navigateurs.',
        body: 'Les navigateurs mettent en forme kanji et kana dans des segments séparés : la police ne voit jamais 食 à côté de べる. Les kanji à plusieurs lectures, comme 食, 行 ou 話, y restent nus.',
      },
      {
        title: 'Les niveaux JLPT sont une estimation.',
        body: 'Il n’existe plus de liste officielle de vocabulaire depuis 2010. Dandan s’appuie sur les listes de Jonathan Waller, qui classent par exemple 日本 en N3 et ne contiennent pas 日本語.',
      },
      {
        title: 'Le fichier est lourd.',
        body: 'Environ 1,8 Mo de WOFF2 pour le dictionnaire complet. Compilez avec --dictionary common (environ 1,3 Mo) ou --max-words pour l’alléger.',
      },
      {
        title: 'Un retour à la ligne peut couper un mot.',
        body: 'Si une ligne se coupe au milieu de 提案, chaque moitié est mise en forme seule et peut recevoir sa propre lecture. word-break: auto-phrase (Chromium, avec lang="ja") coupe plutôt entre les groupes de mots.',
      },
      {
        title: 'Une police par sens (ou Duo), hiragana, JIS X 0208.',
        body: 'Dandan reste nue en texte vertical, car les moteurs de rendu ignorent calt en écriture verticale : le vertical demande Dandan Vertical, ou Dandan Duo, qui couvre les deux sens avec moins de mots rares. Les lectures sont uniquement en hiragana, avec une seule graisse par compilation, et les mots contenant un kanji hors JIS X 0208 (ainsi que 𠮟, 塡, 剝, 頰) n’en reçoivent aucune.',
      },
    ],
  },
  credits: {
    eyebrow: 'Crédits',
    title: 'Bâti sur des travaux ouverts.',
    thanks: 'Merci à',
    items: [
      '<a href="https://furifont.antfu.me/">Furifont</a> d’Anthony Fu, qui a tout inspiré : des furigana dessinés par la police elle-même, et le constat que les navigateurs mettent en forme kanji et kana séparément. Dandan en est une réalisation indépendante et ne partage aucun code avec lui.',
      '<a href="https://fonts.google.com/noto/specimen/Noto+Sans+JP">Noto Sans JP</a> d’Adobe et Google, pour les contours.',
      '<a href="https://www.edrdg.org/jmdict/j_jmdict.html">JMdict</a> de l’Electronic Dictionary Research and Development Group, pour les mots et leurs lectures.',
      '<a href="https://github.com/Doublevil/JmdictFurigana">JmdictFurigana</a> de Doublevil, pour savoir quels kana placer sur quels kanji.',
      '<a href="https://github.com/stephenmk/yomitan-jlpt-vocab">yomitan-jlpt-vocab</a> de stephenmk, tiré des <a href="http://www.tanos.co.uk/jlpt/">listes JLPT</a> de Jonathan Waller, pour les niveaux.',
      '<a href="https://github.com/fonttools/fonttools">fontTools</a> et <a href="https://harfbuzz.github.io/">HarfBuzz</a>, pour la compiler et la tester.',
    ],
    licences: 'Licences',
    font: 'Police',
    fontBody:
      '<a href="fonts/OFL.txt">SIL Open Font License 1.1</a>. Dérivée de Noto Sans JP, © 2014-2021 Adobe, dont le nom réservé (Reserved Font Name) est « Source » ; la famille s’appelle donc Dandan.',
    data: 'Données de lecture',
    dataBody:
      '<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>, issues de JMdict (EDRDG), JmdictFurigana et yomitan-jlpt-vocab, et intégrées à la police sous forme de tables de lecture. Voir <a href="fonts/NOTICE.txt">NOTICE.txt</a>.',
    code: 'Code',
    codeBody: 'MIT, Alexis MABANZA.',
  },
  footer: {
    sign: 'Dandan, pas à pas. 2026, Alexis MABANZA.',
    setIn: 'Composé en Dandan et Instrument Serif.',
    source: 'Code source',
    top: 'Haut de page',
  },
}

// Espace fine insécable (U+202F) avant ; ! ? et dans les guillemets,
// espace insécable (U+00A0) avant le deux-points.
function spaced(text: string): string {
  return text
    .replace(/ ([;!?»])/g, ' $1')
    .replace(/« /g, '« ')
    .replace(/ :/g, ' :')
}

function frenchSpacing<T>(value: T): T {
  if (typeof value === 'string') return spaced(value) as T
  if (typeof value === 'function') {
    const fn = value as (...args: never[]) => unknown
    return ((...args: never[]) => frenchSpacing(fn(...args))) as T
  }
  if (Array.isArray(value)) return value.map(frenchSpacing) as T
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, frenchSpacing(v)])) as T
  }
  return value
}

export default frenchSpacing(fr)
