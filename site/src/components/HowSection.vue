<script setup>
import { computed } from 'vue'
import { FONT } from '../data.js'
import { useI18n } from '../i18n/index.ts'

const { t, locale } = useI18n()

// Feature settings shown for each stage of 日本語を勉強; the copy is in src/i18n (how.stages).
const STAGE_CSS = ['"calt" 0', 'normal', '"ss05" 1']
const MAX_GLYPHS = 65535

const n = computed(() => new Intl.NumberFormat(locale.value))
const reserve = MAX_GLYPHS - FONT.totalGlyphs
const budget = [
  { key: 'base', value: FONT.baseGlyphs },
  { key: 'words', value: FONT.annotated },
  { key: 'free', value: reserve },
]
const budgetLabel = computed(() =>
  t('how.budgetAria', n.value.format(FONT.baseGlyphs), n.value.format(FONT.annotated), n.value.format(reserve), n.value.format(MAX_GLYPHS)),
)
</script>

<template>
  <section id="how" class="section" aria-labelledby="how-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">02</span> · {{ t('how.eyebrow') }}</p>
        <h2 id="how-title">{{ t('how.title') }}</h2>
        <p>{{ t('how.intro') }}</p>
      </div>

      <ol class="flow" :aria-label="t('how.flow')">
        <li v-for="(stage, i) in t('how.stages')" :key="i" class="stage">
          <div class="stage-top">
            <span class="step-no">{{ i + 1 }}</span>
            <code>{{ stage.tag }}</code>
          </div>
          <p class="glyphs jp" lang="ja" :style="{ fontFeatureSettings: STAGE_CSS[i] }">日本語を勉強</p>
          <h3>{{ stage.title }}</h3>
          <p class="body">{{ stage.body }}</p>
        </li>
      </ol>

      <div class="details">
        <div class="lookups">
          <h3>{{ t('how.rulesTitle') }}</h3>
          <ol>
            <!-- Static copy from src/i18n, never user input. -->
            <li v-for="(rule, i) in t('how.rules')" :key="i" v-html="rule" />
          </ol>
          <p class="note">{{ t('how.note') }}</p>
        </div>

        <div class="budget">
          <h3>{{ t('how.budgetTitle') }}</h3>
          <p>{{ t('how.budget', n.format(MAX_GLYPHS), n.format(FONT.candidates)) }}</p>
          <div class="bar" role="img" :aria-label="budgetLabel">
            <span v-for="part in budget" :key="part.key" :class="part.key" :style="{ flexGrow: part.value }" />
          </div>
          <dl class="legend">
            <div v-for="part in budget" :key="part.key">
              <dt><span class="swatch" :class="part.key" />{{ t(`how.budgetParts.${part.key}`) }}</dt>
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

.lookups li :deep(code) {
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
