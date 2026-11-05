<script setup>
import { computed, onMounted, ref } from 'vue'
import { useCopy } from '../composables/useCopy.js'
import { PRESETS, featureValue } from '../data.js'
import FuriSwitch from './FuriSwitch.vue'
import LevelStairs from './LevelStairs.vue'

const preset = ref(PRESETS[0].id)
const text = ref(PRESETS[0].text)
const level = ref(0)
const on = ref(true)
const size = ref(32)
const leading = ref(2)
const { copied, copy } = useCopy()

const features = computed(() => featureValue(level.value, on.value))
const css = computed(
  () => `font-family: "Dandan";\nfont-size: ${size.value}px;\nline-height: ${leading.value.toFixed(1)};\nfont-feature-settings: ${features.value};`,
)
const edited = computed(() => text.value !== PRESETS.find(p => p.id === preset.value)?.text)

// Start smaller on phones, where 32px leaves about nine characters a line.
onMounted(() => {
  if (window.matchMedia('(max-width: 600px)').matches) size.value = 24
})

function choose(p) {
  preset.value = p.id
  text.value = p.text
}
</script>

<template>
  <section id="playground" class="section" aria-labelledby="playground-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">01</span> · Playground</p>
        <h2 id="playground-title">Type anything. The font does the rest.</h2>
        <p>
          The box below is a plain <code>&lt;textarea&gt;</code> set in Dandan. Paste a paragraph, pick the level
          you read at, and watch which words keep their readings.
        </p>
      </div>

      <div class="board">
        <div class="panel">
          <fieldset class="field">
            <legend>Sample text</legend>
            <div class="presets">
              <button
                v-for="p in PRESETS"
                :key="p.id"
                type="button"
                class="chip"
                :aria-pressed="preset === p.id && !edited"
                @click="choose(p)"
              >
                {{ p.label }}
              </button>
            </div>
            <p class="hint">{{ PRESETS.find(p => p.id === preset)?.hint }}{{ edited ? ' · edited' : '' }}</p>
          </fieldset>

          <LevelStairs v-model="level" :muted="!on" compact label="I already know" />

          <FuriSwitch v-model="on" />

          <div class="field">
            <label for="pg-size">Size <output for="pg-size">{{ size }} px</output></label>
            <input id="pg-size" v-model.number="size" type="range" min="16" max="72" step="1" />
          </div>

          <div class="field">
            <label for="pg-leading">Line height <output for="pg-leading">{{ leading.toFixed(1) }}</output></label>
            <input id="pg-leading" v-model.number="leading" type="range" min="1.7" max="2.6" step="0.1" />
          </div>
        </div>

        <div class="editor">
          <label for="pg-text" class="sr-only">Japanese text set in Dandan</label>
          <textarea
            id="pg-text"
            v-model="text"
            class="jp"
            lang="ja"
            spellcheck="false"
            :style="{ fontSize: size + 'px', lineHeight: leading, fontFeatureSettings: features }"
          />
          <div class="editor-bar">
            <pre class="css"><code>{{ css }}</code></pre>
            <button type="button" class="chip" @click="copy(css)">{{ copied ? 'Copied' : 'Copy CSS' }}</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.board {
  display: grid;
  border: 1px solid var(--rule);
  border-radius: var(--r-lg);
  overflow: hidden;
  background: var(--paper-2);
}

@media (min-width: 960px) {
  .board {
    grid-template-columns: 320px 1fr;
  }
}

.panel {
  order: 2;
  display: grid;
  align-content: start;
  gap: 28px;
  padding: 24px;
}

@media (max-width: 959px) {
  .panel {
    border-top: 1px solid var(--rule);
  }
}

@media (min-width: 960px) {
  .panel {
    order: 0;
    border-bottom: 0;
    border-right: 1px solid var(--rule);
  }
}

.field {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}

.field legend,
.field label {
  display: flex;
  justify-content: space-between;
  padding: 0;
  margin-bottom: 10px;
  font: 500 13px/1.4 var(--f-ui);
  color: var(--ink-2);
}

.field label {
  margin-bottom: 0;
}

output {
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}

.presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hint {
  font-size: 13px;
  color: var(--ink-2);
}

input[type='range'] {
  width: 100%;
  margin: 0;
  height: 28px;
  accent-color: var(--shu);
  cursor: pointer;
}

.editor {
  display: grid;
  grid-template-rows: 1fr auto;
  min-width: 0;
  background: var(--paper);
}

textarea {
  display: block;
  width: 100%;
  min-height: 360px;
  padding: 32px;
  border: 0;
  resize: vertical;
  background: transparent;
  color: var(--ink);
  font-family: var(--f-jp);
}

textarea:focus-visible {
  outline: 2px solid var(--shu);
  outline-offset: -6px;
  border-radius: 8px;
}

@media (max-width: 767px) {
  textarea {
    min-height: 320px;
    padding: 20px 16px;
  }
}

.editor-bar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid var(--rule);
}

.css {
  margin: 0;
  min-width: 0;
  overflow-x: auto;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--ink-2);
}
</style>
