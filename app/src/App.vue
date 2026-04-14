<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import MeshGradient from './components/MeshGradient.vue'
import BlobBackground from './components/BlobBackground.vue'
import DiagonalBackground from './components/DiagonalBackground.vue'
import SpikeBackground from './components/SpikeBackground.vue'
import { useTheme } from './composables/useTheme'
import { useAnimation } from './composables/useAnimation'

const { current: theme } = useTheme()
const { current: animation } = useAnimation()

const scrollY = ref(0)
function onScroll() { scrollY.value = window.scrollY }
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const fadeBgs = { midnight: '#0c0c0e', dawn: '#110d0a', daylight: '#0e0f12', dusk: '#0c0a10', aurora: '#080b12' }
const fadeBg = computed(() => fadeBgs[theme.value] || '#0c0c0e')
</script>

<template>
  <div class="layout">
    <div class="parallax-bg" :style="{ transform: `translateY(${scrollY * -0.3}px)` }">
      <MeshGradient v-if="animation === 'ribbons'" :key="'r-'+theme" :palette="theme" />
      <BlobBackground v-else-if="animation === 'blob'" :key="'b-'+theme" :palette="theme" />
      <DiagonalBackground v-else-if="animation === 'diagonal'" :key="'d-'+theme" :palette="theme" />
      <SpikeBackground v-else-if="animation === 'spikes'" :key="'s-'+theme" :palette="theme" />
      <div class="ribbon-fade" :style="{ background: `linear-gradient(to bottom, transparent 0%, ${fadeBg} 80%)` }"></div>
    </div>
    <div class="foreground">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.layout { min-height: 100vh; position: relative; }
.parallax-bg {
  position: fixed; top: 0; left: 0; width: 100%; height: 100vh;
  z-index: 0; will-change: transform;
}
.ribbon-fade {
  position: absolute; bottom: 0; left: 0; width: 100%; height: 60%;
  pointer-events: none;
}
.foreground { position: relative; z-index: 1; min-height: 100vh; }
</style>
