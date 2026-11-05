import { ref } from 'vue'

// 'loading' until Dandan.woff2 (about 1.8 MB) is usable, then 'ready' or 'error'.
// The text shows in a fallback Japanese font meanwhile (font-display: swap).
const status = ref('loading')
let started = false

export function useFontStatus() {
  if (!started && typeof document !== 'undefined' && document.fonts) {
    started = true
    document.fonts
      .load('32px Dandan', '今日')
      .then(faces => {
        status.value = faces.length > 0 ? 'ready' : 'error'
      })
      .catch(() => {
        status.value = 'error'
      })
  }
  return status
}
