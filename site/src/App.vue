<script setup>
import CreditsSection from './components/CreditsSection.vue'
import HeroSection from './components/HeroSection.vue'
import HowSection from './components/HowSection.vue'
import LimitsSection from './components/LimitsSection.vue'
import PlaygroundSection from './components/PlaygroundSection.vue'
import SiteFooter from './components/SiteFooter.vue'
import SiteHeader from './components/SiteHeader.vue'
import UseSection from './components/UseSection.vue'
</script>

<template>
  <a class="skip" href="#main">Skip to content</a>
  <div id="top" />
  <SiteHeader />
  <main id="main">
    <HeroSection />
    <PlaygroundSection />
    <HowSection />
    <UseSection />
    <LimitsSection />
    <CreditsSection />
  </main>
  <SiteFooter />
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
