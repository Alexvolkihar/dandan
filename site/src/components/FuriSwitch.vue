<script setup>
const on = defineModel({ type: Boolean, default: true })
defineProps({ label: { type: String, default: 'Furigana' } })
</script>

<template>
  <button type="button" role="switch" class="switch" :aria-checked="on" @click="on = !on">
    <span class="switch-label">{{ label }}</span>
    <span class="knob-track" aria-hidden="true"><span class="knob" /></span>
    <span class="state" aria-hidden="true">{{ on ? 'On' : 'Off' }}</span>
  </button>
</template>

<style scoped>
.switch {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  padding: 0;
  border: 0;
  background: none;
  color: var(--ink);
  font: 500 14px/1 var(--f-ui);
  cursor: pointer;
}

.knob-track {
  position: relative;
  width: 40px;
  height: 24px;
  border-radius: 999px;
  background: var(--paper-3);
  box-shadow: inset 0 0 0 1px var(--rule-strong);
  transition: background-color 150ms var(--ease);
}

.knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--paper);
  box-shadow: 0 1px 2px #0003, inset 0 0 0 1px var(--rule-strong);
  transition: transform 160ms var(--ease);
}

.switch[aria-checked='true'] .knob-track {
  background: var(--shu);
  box-shadow: none;
}

.switch[aria-checked='true'] .knob {
  transform: translateX(16px);
  box-shadow: 0 1px 2px #0003;
}

.state {
  min-width: 2.2em;
  color: var(--ink-2);
  font-weight: 400;
}
</style>
