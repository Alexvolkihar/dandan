<script setup>
import { computed, useId } from 'vue'
import { LEVELS } from '../data.js'

// A range input (0-5) drawn as a flight of stairs: each step up hides the
// readings of one more JLPT level. The native input stays on top, invisible,
// so pointer, touch and keyboard all work as for any slider.
const model = defineModel({ type: Number, default: 0 })
const props = defineProps({
  label: { type: String, default: 'I already know' },
  muted: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
})

const id = useId()
const valueText = computed(() => {
  const level = LEVELS[model.value]
  return model.value === 0
    ? 'None: every reading shown'
    : `${level.id}: readings of ${level.hides} hidden`
})
</script>

<template>
  <div class="stairs" :class="{ muted: props.muted, compact: props.compact }">
    <label :for="id" class="stairs-label">{{ props.label }}</label>
    <div class="track">
      <div class="steps" aria-hidden="true">
        <div
          v-for="(level, i) in LEVELS"
          :key="level.id"
          class="step"
          :class="{ on: i <= model, current: i === model }"
          :style="{ '--i': i }"
        >
          <span class="step-name">{{ level.short }}</span>
          <span class="tread" />
        </div>
      </div>
      <input
        :id="id"
        v-model.number="model"
        type="range"
        min="0"
        max="5"
        step="1"
        :aria-valuetext="valueText"
      />
    </div>
  </div>
</template>

<style scoped>
.stairs {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.stairs-label {
  font: 500 13px/1.4 var(--f-ui);
  color: var(--ink-2);
}

.track {
  position: relative;
  border-radius: var(--r-sm);
}

.track:has(input:focus-visible) {
  outline: 2px solid var(--shu);
  outline-offset: 6px;
}

.steps {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  align-items: end;
  gap: 4px;
}

.step {
  display: grid;
  gap: 6px;
  justify-items: center;
}

.step-name {
  font: 500 13px/1 var(--f-ui);
  color: var(--ink-2);
  font-variant-numeric: tabular-nums;
  transition: color 150ms var(--ease);
}

.step.on .step-name {
  color: var(--ink);
}

.step.current .step-name {
  color: var(--shu);
  font-weight: 650;
}

.tread {
  display: block;
  width: 100%;
  height: calc(10px + var(--i) * 9px);
  border-radius: 3px 3px 0 0;
  background: var(--paper-3);
  box-shadow: inset 0 0 0 1px var(--rule-strong);
  transform-origin: bottom;
  transition: background-color 200ms var(--ease), box-shadow 200ms var(--ease);
}

.compact .tread {
  height: calc(6px + var(--i) * 6px);
}

.step.on .tread {
  background: var(--ink);
  box-shadow: none;
}

.step.current .tread {
  background: var(--shu);
}

.muted .step.on .tread {
  background: var(--rule-strong);
}

.muted .step.current .tread {
  background: var(--ink-3);
}

input[type='range'] {
  position: absolute;
  inset: -8px 0 -4px;
  width: 100%;
  height: calc(100% + 12px);
  margin: 0;
  opacity: 0;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
}

input[type='range']::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 4px;
  height: 44px;
}

input[type='range']::-moz-range-thumb {
  width: 4px;
  height: 44px;
  border: 0;
}
</style>
