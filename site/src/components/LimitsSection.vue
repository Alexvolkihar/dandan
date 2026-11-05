<script setup>
import { t } from '../i18n/index.ts'
</script>

<template>
  <section id="limits" class="section" aria-labelledby="limits-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">04</span> · {{ t('limits.eyebrow') }}</p>
        <h2 id="limits-title">{{ t('limits.title') }}</h2>
        <p>{{ t('limits.intro') }}</p>
      </div>
      <dl class="limits">
        <div v-for="(item, i) in t('limits.items')" :key="i" class="item">
          <dt>{{ item.title }}</dt>
          <dd>{{ item.body }}</dd>
        </div>
      </dl>
    </div>
  </section>
</template>

<style scoped>
.limits {
  display: grid;
  gap: 0 48px;
  margin: 0;
}

@media (min-width: 900px) {
  .limits {
    grid-template-columns: 1fr 1fr;
  }
}

.item {
  display: grid;
  align-content: start;
  gap: 6px;
  padding: 20px 0;
  border-top: 1px solid var(--rule);
}

dt {
  font: 400 24px/1.2 var(--f-display);
}

dd {
  margin: 0;
  color: var(--ink-2);
  max-width: 60ch;
}
</style>
