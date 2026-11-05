<script setup>
import { FONT } from '../data.js'

const stages = [
  {
    tag: 'Input',
    css: '"calt" 0',
    title: 'Plain text',
    body: 'Unicode, nothing else. The browser cuts it into runs by script before shaping: 日本語 · を · 勉強.',
  },
  {
    tag: 'calt · words',
    css: 'normal',
    title: 'Longest match',
    body: 'Each run of two or more kanji is a ligature. The longest is tried first, so 日本語 is one glyph, never 日本 + 語.',
  },
  {
    tag: 'ss05 · hide N5',
    css: '"ss05" 1',
    title: 'Known words go bare',
    body: '勉強 is an N5 word: after the match, ss05 swaps its glyph back to plain 勉 and 強. 日本語 is not on any list and keeps its reading.',
  },
]

const n = new Intl.NumberFormat('en')
const reserve = 65535 - FONT.totalGlyphs
const budget = [
  { label: 'Base font', value: FONT.baseGlyphs, cls: 'base' },
  { label: 'Annotated words', value: FONT.annotated, cls: 'words' },
  { label: 'Free', value: reserve, cls: 'free' },
]
</script>

<template>
  <section id="how" class="section" aria-labelledby="how-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">02</span> · How it works</p>
        <h2 id="how-title">One glyph per word, read and drawn in advance.</h2>
        <p>
          Every common kanji word, with its reading, is a glyph of its own: the kanji, with the kana at half size
          above them. OpenType rules pick that glyph when the word appears, and stylistic sets put the plain kanji
          back for the words you know.
        </p>
      </div>

      <ol class="flow" aria-label="What happens to 日本語を勉強">
        <li v-for="(stage, i) in stages" :key="stage.tag" class="stage">
          <div class="stage-top">
            <span class="step-no">{{ i + 1 }}</span>
            <code>{{ stage.tag }}</code>
          </div>
          <p class="glyphs jp" lang="ja" :style="{ fontFeatureSettings: stage.css }">日本語を勉強</p>
          <h3>{{ stage.title }}</h3>
          <p class="body">{{ stage.body }}</p>
        </li>
      </ol>

      <div class="details">
        <div class="lookups">
          <h3>Rules, in order</h3>
          <ol>
            <li><code>words</code> ligatures of two or more kanji, longest first.</li>
            <li>
              <code>okurigana</code> a lone kanji before a given kana takes that word's reading (食 + べ: た). Browsers
              shape kanji and kana apart, so only other shapers see this one.
            </li>
            <li><code>kanji</code> a lone kanji takes its one unambiguous reading (見 : み).</li>
            <li>
              <code>hide N5</code> … <code>hide N1</code> turn the glyph of a listed word back into its plain kanji.
              <code>ss05</code> runs the first, <code>ss01</code> all five.
            </li>
          </ol>
          <p class="note">
            A reading is kept only when it clearly wins: lone 食 can be た, く or しょく, so it stays bare. When a reading
            fits over each kanji it sits there (日 本 語); otherwise it is centred and condensed over the word, so it never
            spills into the next one.
          </p>
        </div>

        <div class="budget">
          <h3>The glyph budget</h3>
          <p>
            A font holds at most 65,535 glyphs. The dictionary offers {{ n.format(FONT.candidates) }} words; JLPT words go
            first, then common JMdict words by frequency, until the font is full.
          </p>
          <div
            class="bar"
            role="img"
            :aria-label="`${n.format(FONT.baseGlyphs)} base glyphs, ${n.format(FONT.annotated)} annotated words, ${reserve} free, out of 65,535`"
          >
            <span v-for="part in budget" :key="part.cls" :class="part.cls" :style="{ flexGrow: part.value }" />
          </div>
          <dl class="legend">
            <div v-for="part in budget" :key="part.cls">
              <dt><span class="swatch" :class="part.cls" />{{ part.label }}</dt>
              <dd>{{ n.format(part.value) }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.flow {
  display: grid;
  gap: 16px;
  margin: 0 0 56px;
  padding: 0;
  list-style: none;
  counter-reset: none;
}

@media (min-width: 900px) {
  .flow {
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
  }
}

.stage {
  position: relative;
  display: grid;
  align-content: start;
  gap: 12px;
  padding: 24px;
  border: 1px solid var(--rule);
  background: var(--paper-2);
}

.stage:first-child {
  border-radius: var(--r-lg) var(--r-lg) 0 0;
}

.stage:last-child {
  border-radius: 0 0 var(--r-lg) var(--r-lg);
}

@media (max-width: 899px) {
  .flow {
    gap: 0;
  }

  .stage + .stage {
    border-top: 0;
  }
}

@media (min-width: 900px) {
  .stage + .stage {
    border-left: 0;
  }

  .stage:first-child {
    border-radius: var(--r-lg) 0 0 var(--r-lg);
  }

  .stage:last-child {
    border-radius: 0 var(--r-lg) var(--r-lg) 0;
  }

  /* An arrow between the stages */
  .stage + .stage::before {
    content: '';
    position: absolute;
    top: 50%;
    left: -9px;
    width: 16px;
    height: 16px;
    border-top: 1px solid var(--rule);
    border-right: 1px solid var(--rule);
    background: var(--paper-2);
    transform: translateY(-50%) rotate(45deg);
  }
}

.stage-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-no {
  display: inline-grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--ink);
  color: var(--paper);
  font: 600 12px/1 var(--f-ui);
}

.glyphs {
  margin: 8px 0 4px;
  font-size: clamp(30px, 3.4vw, 40px);
  line-height: 1.8;
  white-space: nowrap;
}

.stage h3 {
  font-size: 26px;
}

.body {
  font-size: 15px;
  color: var(--ink-2);
}

.details {
  display: grid;
  gap: 48px;
}

@media (min-width: 900px) {
  .details {
    grid-template-columns: 1fr 1fr;
    gap: 64px;
  }
}

.details h3 {
  font-size: 28px;
  margin-bottom: 16px;
}

.lookups ol {
  display: grid;
  gap: 10px;
  margin: 0 0 20px;
  padding-left: 1.4em;
}

.lookups li::marker {
  color: var(--ink-2);
  font-variant-numeric: tabular-nums;
}

.lookups li code {
  margin-right: 4px;
}

.note,
.budget p {
  color: var(--ink-2);
}

.bar {
  display: flex;
  height: 14px;
  margin: 24px 0 16px;
  border-radius: 4px;
  overflow: hidden;
  gap: 2px;
}

.bar span {
  flex-basis: 0;
  min-width: 3px;
}

.base {
  background: var(--ink);
}

.words {
  background: var(--shu);
}

.free {
  background: var(--rule-strong);
}

.legend {
  display: grid;
  gap: 6px;
  margin: 0;
}

.legend div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding-block: 6px;
  border-bottom: 1px solid var(--rule);
  font-size: 14px;
}

.legend dt {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--ink-2);
}

.legend dd {
  margin: 0;
  font-variant-numeric: tabular-nums;
}

.swatch {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}
</style>
