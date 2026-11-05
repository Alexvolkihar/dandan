import { onMounted, onUnmounted, ref } from 'vue'

export function useReducedMotion() {
  const reduced = ref(false)
  let media
  const sync = () => (reduced.value = media.matches)
  onMounted(() => {
    media = window.matchMedia('(prefers-reduced-motion: reduce)')
    sync()
    media.addEventListener('change', sync)
  })
  onUnmounted(() => media?.removeEventListener('change', sync))
  return reduced
}
