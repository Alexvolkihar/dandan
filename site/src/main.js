import { createApp } from 'vue'
import '@fontsource/instrument-serif/latin-400.css'
import '@fontsource/instrument-serif/latin-400-italic.css'
import './style.css'
import App from './App.vue'
import { initI18n } from './i18n/index.ts'

// Load the visitor's language first, so the page never flashes in English.
await initI18n()
createApp(App).mount('#app')
