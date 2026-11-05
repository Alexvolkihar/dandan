import { ref } from 'vue'

export function useCopy() {
  const copied = ref(false)
  let timer

  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text)
      copied.value = true
      clearTimeout(timer)
      timer = setTimeout(() => (copied.value = false), 1600)
    } catch {
      copied.value = false
    }
  }

  return { copied, copy }
}
