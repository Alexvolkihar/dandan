<script setup>
import { useTheme } from '../composables/useTheme.js'
import { REPO_URL } from '../data.js'

const { dark, toggle } = useTheme()
</script>

<template>
  <header class="header">
    <div class="wrap bar">
      <a class="brand" href="#top" aria-label="Dandan, back to top">
        <span class="mark jp" lang="ja" aria-hidden="true">段々</span>
        <span class="name">Dandan</span>
      </a>
      <nav aria-label="Sections">
        <ul>
          <li class="wide"><a href="#playground">Playground</a></li>
          <li class="wide"><a href="#how">How it works</a></li>
          <li class="wide"><a href="#use">Use it</a></li>
          <li class="wide"><a href="#limits">Limits</a></li>
          <li v-if="REPO_URL" class="wide"><a :href="REPO_URL">Source</a></li>
          <li><a class="chip" href="#download">Download</a></li>
          <li>
            <button
              type="button"
              class="theme"
              :aria-label="dark ? 'Switch to light theme' : 'Switch to dark theme'"
              @click="toggle"
            >
              <svg v-if="dark" width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
                <circle cx="9" cy="9" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5" />
                <path d="M9 1.5v2M9 14.5v2M1.5 9h2M14.5 9h2M3.7 3.7l1.4 1.4M12.9 12.9l1.4 1.4M3.7 14.3l1.4-1.4M12.9 5.1l1.4-1.4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
                <path d="M15 10.6A6.5 6.5 0 0 1 7.4 3a6.5 6.5 0 1 0 7.6 7.6Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" />
              </svg>
            </button>
          </li>
        </ul>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: color-mix(in srgb, var(--paper) 92%, transparent);
  border-bottom: 1px solid var(--rule);
}

@supports (backdrop-filter: blur(1px)) {
  .header {
    background: color-mix(in srgb, var(--paper) 82%, transparent);
    backdrop-filter: saturate(1.2) blur(10px);
  }
}

.bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 64px;
}

.brand {
  display: inline-flex;
  align-items: flex-end;
  gap: 10px;
  text-decoration: none;
}

.mark {
  font-size: 22px;
  line-height: 1.7;
  color: var(--shu);
}

.name {
  font: 400 26px/1.4 var(--f-display);
}

ul {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}

nav a:not(.chip) {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0 10px;
  font-size: 14px;
  color: var(--ink-2);
  text-decoration: none;
}

nav a:not(.chip):hover {
  color: var(--ink);
}

nav .chip {
  margin-left: 8px;
  text-decoration: none;
  color: var(--ink);
}

.theme {
  display: inline-grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border: 0;
  border-radius: 50%;
  background: none;
  color: var(--ink-2);
  cursor: pointer;
  transition: color 150ms var(--ease), transform 120ms var(--ease);
}

.theme:hover {
  color: var(--ink);
}

.theme:active {
  transform: scale(0.96);
}

@media (max-width: 860px) {
  .wide {
    display: none;
  }
}
</style>
