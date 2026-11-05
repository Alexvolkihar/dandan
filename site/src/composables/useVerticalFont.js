import { ref } from 'vue'
import { VERTICAL_FONT } from '../data.js'

// Dandan Vertical (about 2 MB) is only fetched when someone asks for vertical
// text: load() registers the face with the FontFace API the first time.
// status: 'idle' until then, 'loading', then 'ready' or 'error'.
const status = ref('idle')

export function useVerticalFont() {
  function load() {
    if (status.value !== 'idle' && status.value !== 'error') return
    if (typeof FontFace === 'undefined' || !document.fonts) {
      status.value = 'error'
      return
    }
    status.value = 'loading'
    const url = new URL(VERTICAL_FONT.woff2, document.baseURI).href
    const face = new FontFace(VERTICAL_FONT.family, `url("${url}") format("woff2")`, { display: 'swap' })
    document.fonts.add(face)
    face
      .load()
      .then(() => {
        status.value = 'ready'
      })
      .catch(() => {
        document.fonts.delete(face)
        status.value = 'error'
      })
  }
  return { status, load }
}
