<script setup>
import { t } from '../i18n/index.ts'
</script>

<template>
  <section id="credits" class="section" aria-labelledby="credits-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">05</span> · {{ t('credits.eyebrow') }}</p>
        <h2 id="credits-title">{{ t('credits.title') }}</h2>
      </div>
      <!-- Static copy from src/i18n, never user input. -->
      <div class="cols">
        <div>
          <h3>{{ t('credits.thanks') }}</h3>
          <ul>
            <li v-for="(item, i) in t('credits.items')" :key="i" v-html="item" />
          </ul>
        </div>
        <div>
          <h3>{{ t('credits.licences') }}</h3>
          <dl>
            <div>
              <dt>{{ t('credits.font') }}</dt>
              <dd v-html="t('credits.fontBody')" />
            </div>
            <div>
              <dt>{{ t('credits.data') }}</dt>
              <dd v-html="t('credits.dataBody')" />
            </div>
            <div>
              <dt>{{ t('credits.code') }}</dt>
              <dd>{{ t('credits.codeBody') }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cols {
  display: grid;
  gap: 48px;
}

@media (min-width: 900px) {
  .cols {
    grid-template-columns: 1.2fr 1fr;
    gap: 64px;
  }
}

h3 {
  font-size: 28px;
  margin-bottom: 16px;
}

ul {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

li {
  padding-left: 18px;
  position: relative;
  color: var(--ink-2);
}

li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.7em;
  width: 8px;
  height: 1px;
  background: var(--shu);
}

li :deep(a),
dd :deep(a) {
  color: var(--ink);
}

dl {
  display: grid;
  margin: 0;
}

dl div {
  display: grid;
  gap: 4px;
  padding: 14px 0;
  border-top: 1px solid var(--rule);
}

dt {
  font-weight: 600;
  font-size: 14px;
}

dd {
  margin: 0;
  color: var(--ink-2);
}
</style>
