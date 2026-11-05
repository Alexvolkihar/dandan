<script setup>
import { computed, ref } from 'vue'
import { useCopy } from '../composables/useCopy.js'
import { useFontStatus } from '../composables/useFontStatus.js'
import { FONT, HERO_LINES, HERO_WORDS, LEVELS, featureValue, mebibytes } from '../data.js'
import FadingText from './FadingText.vue'
import FuriSwitch from './FuriSwitch.vue'
import LevelStairs from './LevelStairs.vue'

const level = ref(0)
const on = ref(true)
const fontStatus = useFontStatus()
const { copied, copy } = useCopy()

const lines = HERO_LINES.map(line => line.text)
const features = computed(() => featureValue(level.value, on.value))
const rank = computed(() => (on.value ? level.value : 6))
const css = computed(() => `font-feature-settings: ${features.value};`)

const shown = computed(() => (on.value ? HERO_WORDS.filter(([, step]) => step > level.value).length : 0))
const hiddenNow = computed(() => HERO_WORDS.filter(([, step]) => step === level.value).map(([word]) => word))
const status = computed(() => {
  if (!on.value) return 'calt is off, so every reading is gone.'
  if (level.value === 0) return 'Climb the stairs to drop the readings you already know.'
  return `${LEVELS[level.value].id} hides`
})
</script>

<template>
  <section class="hero" aria-labelledby="hero-title">
    <div class="wrap head">
      <div class="title">
        <p class="eyebrow">A free Japanese font · OFL 1.1</p>
        <h1 id="hero-title">Furigana that fade <em>as you learn.</em></h1>
      </div>
      <div class="intro">
        <p class="lede">
          Dandan draws readings over kanji by itself: plain text in, furigana out, with no
          <code>&lt;ruby&gt;</code> and no script. Tell it the JLPT level you know and those words lose
          their readings, one step at a time.
        </p>
        <div class="actions">
          <a class="btn btn-solid" :href="FONT.woff2" download>
            <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
              <path d="M8 2v8m0 0L4.5 6.5M8 10l3.5-3.5M3 13h10" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            Download the font <small>WOFF2 · {{ mebibytes(FONT.woff2Bytes) }} MB</small>
          </a>
          <a class="btn" href="#playground">Try your own text</a>
        </div>
      </div>
    </div>

    <div class="wrap">
      <figure class="specimen" aria-labelledby="specimen-caption">
        <div class="specimen-bar">
          <span id="specimen-caption" class="eyebrow">Specimen · Dandan Regular</span>
          <span class="font-status" :data-status="fontStatus" role="status">
            <span class="dot" aria-hidden="true" />
            <template v-if="fontStatus === 'loading'">Loading the font ({{ mebibytes(FONT.woff2Bytes) }} MB)…</template>
            <template v-else-if="fontStatus === 'ready'">Font loaded</template>
            <template v-else>The font did not load: showing a fallback without furigana</template>
          </span>
        </div>

        <div class="sample jp" :class="{ waiting: fontStatus !== 'ready' }">
          <FadingText :lines="lines" :features="features" :rank="rank" />
        </div>

        <div class="controls">
          <LevelStairs v-model="level" :muted="!on" label="I already know" />
          <p class="tally">
            <span class="big"><span class="num">{{ shown }}</span><span class="of">/{{ HERO_WORDS.length }}</span></span>
            <span class="tally-label">words still show a reading</span>
          </p>
          <div class="readout">
            <FuriSwitch v-model="on" />
            <p class="hides" aria-live="polite">
              <span>{{ status }}</span>
              <template v-if="on && level > 0">
                <span v-for="word in hiddenNow" :key="word" class="word jp-plain" lang="ja">{{ word }}</span>
              </template>
            </p>
            <div class="css-line">
              <code>{{ css }}</code>
              <button type="button" class="chip" @click="copy(css)">
                {{ copied ? 'Copied' : 'Copy CSS' }}
              </button>
            </div>
          </div>
        </div>
      </figure>
    </div>
  </section>
</template>

<style scoped>
.hero {
  padding-block: 40px 96px;
}

.head {
  display: grid;
  gap: 24px;
  margin-bottom: 36px;
}

@media (min-width: 1024px) {
  .head {
    grid-template-columns: 1.1fr 1fr;
    align-items: end;
    gap: 64px;
  }
}

.title {
  display: grid;
  gap: 18px;
}

h1 {
  font-size: clamp(50px, 6vw, 84px);
  line-height: 0.98;
  letter-spacing: -0.01em;
}

h1 em {
  color: var(--shu);
}

.intro {
  display: grid;
  gap: 24px;
  padding-bottom: 8px;
}

.lede {
  font-size: 18px;
  color: var(--ink-2);
  max-width: 46ch;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.specimen {
  margin: 0;
  border: 1px solid var(--rule);
  border-radius: var(--r-lg);
  background: var(--paper-2);
  overflow: hidden;
}

.specimen-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px 16px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--rule);
}

.font-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--ink-2);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ink-3);
}

.font-status[data-status='loading'] .dot {
  background: var(--shu);
  animation: pulse 1.2s var(--ease) infinite alternate;
}

.font-status[data-status='ready'] .dot {
  background: #3f8f5a;
}

@keyframes pulse {
  to {
    opacity: 0.25;
  }
}

.sample {
  padding: clamp(20px, 3vw, 40px) clamp(20px, 4vw, 56px) clamp(16px, 2.4vw, 32px);
  font-size: clamp(22px, 2.9vw, 40px);
  line-height: 1.95;
  color: var(--ink);
  transition: opacity 300ms var(--ease);
}

.sample.waiting {
  opacity: 0.55;
}

.controls {
  display: grid;
  gap: 28px;
  padding: 24px 20px 24px;
  border-top: 1px solid var(--rule);
  background: var(--paper);
}

@media (min-width: 900px) {
  .controls {
    grid-template-columns: minmax(280px, 380px) auto 1fr;
    gap: 40px;
    padding: 28px 32px;
    align-items: end;
  }
}

.tally {
  display: grid;
  gap: 2px;
  min-width: 10ch;
}

.big {
  font: 400 64px/0.9 var(--f-display);
  font-variant-numeric: tabular-nums;
}

.big .of {
  color: var(--ink-3);
  font-size: 0.5em;
  margin-left: 4px;
}

.tally-label {
  font-size: 13px;
  color: var(--ink-2);
}

.readout {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.hides {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  min-height: 30px;
  font-size: 14px;
  color: var(--ink-2);
}

.word {
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--shu-soft);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.5;
}

.css-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
}

.css-line code {
  font-size: 13px;
  white-space: normal;
}
</style>
