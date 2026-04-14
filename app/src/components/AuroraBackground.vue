<template>
  <canvas ref="canvas" class="aurora-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({ palette: { type: String, default: 'midnight' } })
const canvas = ref(null)
let ctx, W = 0, H = 0, rafId, t = 0

// Stars
const STAR_COUNT = 180
let stars = []

function buildStars() {
  stars = Array.from({ length: STAR_COUNT }, () => ({
    x: Math.random(),
    y: Math.random() * 0.7, // upper 70%
    r: 0.4 + Math.random() * 1.2,
    twinkleFreq: 0.002 + Math.random() * 0.006,
    twinklePhase: Math.random() * Math.PI * 2,
    brightness: 0.3 + Math.random() * 0.7,
  }))
}

// Aurora curtain colors per theme
const CURTAINS = {
  midnight: [
    { color: [80, 220, 140], y: 0.18, amp: 40, freq: 0.003, speed: 0.0008, opacity: 0.12 },
    { color: [110, 160, 255], y: 0.25, amp: 50, freq: 0.0025, speed: 0.0006, opacity: 0.10 },
    { color: [180, 100, 240], y: 0.22, amp: 35, freq: 0.0035, speed: 0.001, opacity: 0.08 },
    { color: [255, 140, 80], y: 0.30, amp: 30, freq: 0.002, speed: 0.0007, opacity: 0.06 },
  ],
  dawn: [
    { color: [240, 160, 50], y: 0.20, amp: 45, freq: 0.003, speed: 0.0008, opacity: 0.14 },
    { color: [230, 120, 80], y: 0.28, amp: 40, freq: 0.0025, speed: 0.0006, opacity: 0.10 },
    { color: [200, 150, 90], y: 0.24, amp: 35, freq: 0.0035, speed: 0.001, opacity: 0.08 },
    { color: [180, 100, 60], y: 0.32, amp: 30, freq: 0.002, speed: 0.0007, opacity: 0.06 },
  ],
  daylight: [
    { color: [70, 200, 200], y: 0.18, amp: 40, freq: 0.003, speed: 0.0008, opacity: 0.10 },
    { color: [90, 150, 255], y: 0.25, amp: 50, freq: 0.0025, speed: 0.0006, opacity: 0.08 },
    { color: [80, 210, 160], y: 0.22, amp: 35, freq: 0.0035, speed: 0.001, opacity: 0.07 },
    { color: [120, 190, 130], y: 0.30, amp: 30, freq: 0.002, speed: 0.0007, opacity: 0.05 },
  ],
  dusk: [
    { color: [140, 80, 220], y: 0.18, amp: 45, freq: 0.003, speed: 0.0008, opacity: 0.14 },
    { color: [200, 50, 160], y: 0.25, amp: 40, freq: 0.0025, speed: 0.0006, opacity: 0.10 },
    { color: [100, 60, 200], y: 0.22, amp: 35, freq: 0.0035, speed: 0.001, opacity: 0.09 },
    { color: [220, 70, 120], y: 0.30, amp: 30, freq: 0.002, speed: 0.0007, opacity: 0.06 },
  ],
  aurora: [
    { color: [40, 220, 140], y: 0.15, amp: 55, freq: 0.003, speed: 0.0009, opacity: 0.16 },
    { color: [50, 160, 220], y: 0.22, amp: 45, freq: 0.0025, speed: 0.0007, opacity: 0.12 },
    { color: [80, 240, 180], y: 0.20, amp: 40, freq: 0.004, speed: 0.0011, opacity: 0.10 },
    { color: [100, 80, 240], y: 0.28, amp: 35, freq: 0.002, speed: 0.0006, opacity: 0.08 },
    { color: [40, 200, 200], y: 0.18, amp: 50, freq: 0.0032, speed: 0.0008, opacity: 0.07 },
  ],
}

const curtains = CURTAINS[props.palette] || CURTAINS.aurora

function draw() {
  if (!ctx) return
  ctx.clearRect(0, 0, W, H)

  // Stars
  for (const s of stars) {
    const twinkle = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(t * s.twinkleFreq + s.twinklePhase))
    const alpha = s.brightness * twinkle
    ctx.beginPath()
    ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(220,225,240,${alpha.toFixed(2)})`
    ctx.fill()
  }

  // Aurora curtains — vertical light columns that wave
  for (const c of curtains) {
    const [r, g, b] = c.color
    const baseY = c.y * H

    // Draw multiple vertical strips across the width
    const strips = 60
    ctx.beginPath()

    // Top edge — wavy
    for (let i = 0; i <= strips; i++) {
      const x = (i / strips) * W
      const wave = c.amp * Math.sin(x * c.freq + t * c.speed)
        + c.amp * 0.5 * Math.sin(x * c.freq * 1.7 + t * c.speed * 1.3 + 2.1)
        + c.amp * 0.3 * Math.sin(x * c.freq * 0.6 + t * c.speed * 0.7 + 4.2)
      const y = baseY + wave
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }

    // Bottom edge — wider wave, fades down
    const curtainHeight = H * 0.35
    for (let i = strips; i >= 0; i--) {
      const x = (i / strips) * W
      const wave = c.amp * 0.6 * Math.sin(x * c.freq * 0.8 + t * c.speed * 0.9 + 1.5)
      const y = baseY + curtainHeight + wave
      ctx.lineTo(x, y)
    }
    ctx.closePath()

    // Vertical gradient — bright at top, fading down
    const grad = ctx.createLinearGradient(0, baseY - c.amp, 0, baseY + curtainHeight)
    grad.addColorStop(0, `rgba(${r},${g},${b},0)`)
    grad.addColorStop(0.1, `rgba(${r},${g},${b},${c.opacity * 0.4})`)
    grad.addColorStop(0.25, `rgba(${r},${g},${b},${c.opacity})`)
    grad.addColorStop(0.5, `rgba(${r},${g},${b},${c.opacity * 0.6})`)
    grad.addColorStop(0.75, `rgba(${r},${g},${b},${c.opacity * 0.2})`)
    grad.addColorStop(1, `rgba(${r},${g},${b},0)`)

    ctx.fillStyle = grad
    ctx.fill()
  }

  // Bright column highlights — vertical light rays
  for (let i = 0; i < 8; i++) {
    const phase = i * 1.37 + t * 0.0003
    const x = W * (0.1 + 0.8 * ((Math.sin(phase) + 1) / 2))
    const intensity = 0.5 + 0.5 * Math.sin(t * 0.001 + i * 2.3)
    const c = curtains[i % curtains.length]
    const [r, g, b] = c.color
    const colH = H * 0.5
    const colY = H * 0.05

    const ray = ctx.createLinearGradient(x, colY, x, colY + colH)
    ray.addColorStop(0, `rgba(${r},${g},${b},0)`)
    ray.addColorStop(0.2, `rgba(${r},${g},${b},${0.04 * intensity})`)
    ray.addColorStop(0.5, `rgba(${r},${g},${b},${0.02 * intensity})`)
    ray.addColorStop(1, `rgba(${r},${g},${b},0)`)

    ctx.fillStyle = ray
    ctx.fillRect(x - 20, colY, 40, colH)
  }

  t++
  rafId = requestAnimationFrame(draw)
}

function resize() {
  if (!canvas.value) return
  const dpr = window.devicePixelRatio || 1
  W = canvas.value.offsetWidth; H = canvas.value.offsetHeight
  canvas.value.width = W * dpr; canvas.value.height = H * dpr
  ctx = canvas.value.getContext('2d'); ctx.scale(dpr, dpr)
  buildStars()
}

onMounted(() => { resize(); window.addEventListener('resize', resize); draw() })
onUnmounted(() => { window.removeEventListener('resize', resize); cancelAnimationFrame(rafId) })
</script>

<style scoped>
.aurora-canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; }
</style>
