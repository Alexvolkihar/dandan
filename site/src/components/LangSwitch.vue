<script setup>
import { LOCALES, useI18n } from '../i18n/index.ts'

// Real links (?lang=xx), so they work without JavaScript and can be shared;
// a click switches in place, remembers the choice and updates the URL.
const { t, locale, setLocale } = useI18n()
</script>

<template>
  <div class="langs" role="group" :aria-label="t('header.language')">
    <template v-for="(l, i) in LOCALES" :key="l.code">
      <span v-if="i > 0" class="sep" aria-hidden="true">·</span>
      <a
        :href="`?lang=${l.code}`"
        :hreflang="l.code"
        :lang="l.code"
        :aria-label="l.name"
        :aria-current="l.code === locale ? 'true' : undefined"
        @click.prevent="setLocale(l.code, { remember: true })"
        >{{ l.label }}</a
      >
    </template>
  </div>
</template>

<style scoped>
.langs {
  display: inline-flex;
  align-items: center;
}

a {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0 6px;
  font: 500 13px/1 var(--f-ui);
  color: var(--ink-2);
  text-decoration: none;
  transition: color 150ms var(--ease);
}

.sep {
  color: var(--ink-3);
  font-size: 13px;
}

a:hover {
  color: var(--ink);
}

a[aria-current='true'] {
  color: var(--ink);
  font-weight: 650;
}

a:lang(ja) {
  font-family: var(--f-jp-plain);
}
</style>
