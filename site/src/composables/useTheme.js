import { onMounted, onUnmounted, ref } from 'vue'

const KEY = 'dandan-theme'

function systemDark() {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

// Light or dark; follows the system until the visitor picks one.
export function useTheme() {
  const dark = ref(false)
  let media

  function sync() {
    const saved = document.documentElement.dataset.theme
    dark.value = saved ? saved === 'dark' : systemDark()
  }

  function toggle() {
    const next = dark.value ? 'light' : 'dark'
    document.documentElement.dataset.theme = next
    dark.value = next === 'dark'
    try {
      localStorage.setItem(KEY, next)
    } catch {
      // Storage can be unavailable (private mode); the choice then lasts for this visit.
    }
  }

  onMounted(() => {
    sync()
    media = window.matchMedia?.('(prefers-color-scheme: dark)')
    media?.addEventListener('change', sync)
  })
  onUnmounted(() => media?.removeEventListener('change', sync))

  return { dark, toggle }
}
