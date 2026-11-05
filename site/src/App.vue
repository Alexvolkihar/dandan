<script setup>
import HeroSection from './components/HeroSection.vue'
import SiteHeader from './components/SiteHeader.vue'
</script>

<template>
  <a class="skip" href="#main">Skip to content</a>
  <div id="top" />
  <SiteHeader />
  <main id="main">
    <HeroSection />
  </main>
</template>

<style>
.skip {
  position: absolute;
  left: 16px;
  top: -100px;
  z-index: 20;
  padding: 10px 14px;
  border-radius: var(--r-sm);
  background: var(--ink);
  color: var(--paper);
}

.skip:focus {
  top: 12px;
}
</style>
