<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import MeshGradient from './components/MeshGradient.vue'

const scrollY = ref(0)
function onScroll() { scrollY.value = window.scrollY }
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <div class="layout">
    <!-- Ribbon animation — parallax: moves at 0.3x scroll speed -->
    <div class="parallax-bg" :style="{ transform: `translateY(${scrollY * -0.3}px)` }">
      <MeshGradient />
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
.foreground { position: relative; z-index: 1; min-height: 100vh; }
</style>
