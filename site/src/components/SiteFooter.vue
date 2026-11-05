<script setup>
import { REPO_URL } from '../data.js'
</script>

<template>
  <footer class="footer">
    <div class="wrap row">
      <p class="sign">
        <span class="jp" lang="ja">段々</span>
        <span>Dandan, step by step. 2026, Alexis MABANZA.</span>
      </p>
      <p class="meta">
        Set in Dandan and Instrument Serif.
        <a v-if="REPO_URL" :href="REPO_URL">Source code</a>
        <a href="#top">Back to top</a>
      </p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  border-top: 1px solid var(--rule);
  padding-block: 32px 40px;
  font-size: 14px;
  color: var(--ink-2);
}

.row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px 32px;
}

.sign {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.sign .jp {
  font-size: 24px;
  line-height: 1.8;
  color: var(--shu);
}

.sign span:last-child {
  padding-bottom: 6px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding-bottom: 6px;
}
</style>
