<script setup>
import { ref, watch } from 'vue'
import { useReducedMotion } from '../composables/useReducedMotion.js'

// Lines of Japanese set in Dandan whose furigana fade in or out when the
// feature settings change. Annotated glyphs keep the advance width of their
// kanji, so two copies with different settings line up exactly: the copy that
// shows more readings is cross-faded over a copy that stays put.
const props = defineProps({
  lines: { type: Array, required: true },
  features: { type: String, required: true },
  // How much the settings hide (higher = fewer readings); sets the fade direction.
  rank: { type: Number, required: true },
})

const reduced = useReducedMotion()
const base = ref({ features: props.features })
const overlay = ref(null)
let key = 0

watch(
  () => [props.features, props.rank],
  ([features, rank], [oldFeatures, oldRank]) => {
    const settled = overlay.value?.target ?? oldFeatures
    overlay.value = null
    if (reduced.value || features === settled) {
      base.value = { features }
      return
    }
    key += 1
    if (rank >= oldRank) {
      // Readings disappear: the new settings sit below, the old copy fades out on top.
      base.value = { features }
      overlay.value = { features: settled, target: features, mode: 'out', key }
    } else {
      // Readings appear: the old copy stays below, the new one fades in on top.
      base.value = { features: settled }
      overlay.value = { features, target: features, mode: 'in', key }
    }
  },
)

function settle() {
  if (overlay.value) base.value = { features: overlay.value.target }
  overlay.value = null
}
</script>

<template>
  <div class="fading" lang="ja">
    <div class="layer" :style="{ fontFeatureSettings: base.features }">
      <p v-for="(line, i) in lines" :key="i">{{ line }}</p>
    </div>
    <div
      v-if="overlay"
      :key="overlay.key"
      class="layer overlay"
      :class="overlay.mode"
      :style="{ fontFeatureSettings: overlay.features }"
      aria-hidden="true"
      @animationend="settle"
    >
      <p v-for="(line, i) in lines" :key="i">{{ line }}</p>
    </div>
  </div>
</template>

<style scoped>
.fading {
  display: grid;
}

.layer {
  grid-area: 1 / 1;
  min-width: 0;
}

.layer p {
  margin: 0;
}

.overlay {
  pointer-events: none;
  user-select: none;
}

.overlay.out {
  animation: fade-out 420ms var(--ease) forwards;
}

.overlay.in {
  animation: fade-in 420ms var(--ease) forwards;
}

@keyframes fade-out {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
