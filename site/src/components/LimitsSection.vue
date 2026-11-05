<script setup>
const limits = [
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
    body: "There has been no official vocabulary list since 2010. Dandan uses Jonathan Waller's lists, which put 日本 at N3 and leave 日本語 out, for example.",
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
]
</script>

<template>
  <section id="limits" class="section" aria-labelledby="limits-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">04</span> · Limits</p>
        <h2 id="limits-title">What a font cannot know.</h2>
        <p>Dandan guesses from the dictionary, without grammar or context. Check readings that matter.</p>
      </div>
      <dl class="limits">
        <div v-for="item in limits" :key="item.title" class="item">
          <dt>{{ item.title }}</dt>
          <dd>{{ item.body }}</dd>
        </div>
      </dl>
    </div>
  </section>
</template>

<style scoped>
.limits {
  display: grid;
  gap: 0 48px;
  margin: 0;
}

@media (min-width: 900px) {
  .limits {
    grid-template-columns: 1fr 1fr;
  }
}

.item {
  display: grid;
  align-content: start;
  gap: 6px;
  padding: 20px 0;
  border-top: 1px solid var(--rule);
}

dt {
  font: 400 24px/1.2 var(--f-display);
}

dd {
  margin: 0;
  color: var(--ink-2);
  max-width: 60ch;
}
</style>
