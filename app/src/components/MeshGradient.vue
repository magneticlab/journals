<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
let animId = null
let time = 0

function lerp(a, b, t) { return a + (b - a) * t }

onMounted(() => {
  const c = canvas.value
  if (!c) return
  const ctx = c.getContext('2d')
  let w, h

  function resize() {
    w = c.width = window.innerWidth
    h = c.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)

  // Blob positions — slow drifting
  const blobs = [
    { x: 0.2, y: 0.3, r: 0.35, color: [99, 149, 255] },    // blue
    { x: 0.7, y: 0.2, r: 0.30, color: [52, 211, 153] },     // green
    { x: 0.5, y: 0.7, r: 0.32, color: [167, 139, 250] },    // purple
    { x: 0.8, y: 0.6, r: 0.28, color: [251, 191, 36] },     // amber
  ]

  function draw() {
    time += 0.003
    ctx.clearRect(0, 0, w, h)

    for (const blob of blobs) {
      const bx = (blob.x + Math.sin(time * 0.7 + blob.x * 10) * 0.08) * w
      const by = (blob.y + Math.cos(time * 0.5 + blob.y * 8) * 0.06) * h
      const br = blob.r * Math.min(w, h)

      const grad = ctx.createRadialGradient(bx, by, 0, bx, by, br)
      grad.addColorStop(0, `rgba(${blob.color.join(',')}, 0.08)`)
      grad.addColorStop(0.5, `rgba(${blob.color.join(',')}, 0.03)`)
      grad.addColorStop(1, `rgba(${blob.color.join(',')}, 0)`)

      ctx.fillStyle = grad
      ctx.fillRect(0, 0, w, h)
    }

    animId = requestAnimationFrame(draw)
  }

  draw()

  onUnmounted(() => {
    cancelAnimationFrame(animId)
    window.removeEventListener('resize', resize)
  })
})
</script>

<template>
  <canvas ref="canvas" class="mesh-canvas" />
</template>

<style scoped>
.mesh-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 0;
}
</style>
