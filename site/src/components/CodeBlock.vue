<script setup>
import { useCopy } from '../composables/useCopy.js'

const props = defineProps({
  code: { type: String, required: true },
  label: { type: String, required: true },
})
const { copied, copy } = useCopy()
</script>

<template>
  <div class="code">
    <div class="code-bar">
      <span>{{ props.label }}</span>
      <button type="button" class="chip" @click="copy(props.code)">{{ copied ? 'Copied' : 'Copy' }}</button>
    </div>
    <pre tabindex="0" :aria-label="props.label"><code>{{ props.code }}</code></pre>
  </div>
</template>

<style scoped>
.code {
  border: 1px solid var(--rule);
  border-radius: var(--r-md);
  background: var(--code-bg);
  min-width: 0;
  overflow: hidden;
}

.code-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 8px 8px 16px;
  border-bottom: 1px solid var(--rule);
  font-size: 13px;
  color: var(--ink-2);
}

pre {
  margin: 0;
  padding: 16px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.7;
  color: var(--ink);
}

pre:focus-visible {
  outline-offset: -4px;
}
</style>
