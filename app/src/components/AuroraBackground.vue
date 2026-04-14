<template>
  <canvas ref="canvas" class="aurora-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({ palette: { type: String, default: 'midnight' } })
const canvas = ref(null)
let ctx, W = 0, H = 0, rafId, t = 0

// Stars — sparse, only in the dark areas
const STAR_COUNT = 120
let stars = []

function buildStars() {
  stars = Array.from({ length: STAR_COUNT }, () => ({
    x: Math.random(),
    y: Math.random() * 0.6,
    r: 0.3 + Math.random() * 1.0,
    freq: 0.001 + Math.random() * 0.004,
    phase: Math.random() * Math.PI * 2,
    bright: 0.15 + Math.random() * 0.5,
  }))
}

// Aurora bands — concentrated on the right side
const PALETTES = {
  midnight: [
    [60, 240, 130], [40, 200, 160], [80, 255, 140],
    [50, 180, 220], [100, 220, 180], [70, 255, 160],
  ],
  dawn: [
    [240, 160, 60], [220, 130, 80], [255, 180, 50],
    [200, 140, 100], [230, 150, 70], [255, 170, 40],
  ],
  daylight: [
    [60, 200, 200], [80, 220, 180], [50, 240, 160],
    [70, 180, 220], [90, 210, 190], [60, 230, 170],
  ],
  dusk: [
    [160, 60, 220], [200, 40, 180], [140, 80, 255],
    [180, 50, 200], [220, 70, 160], [130, 60, 240],
  ],
  aurora: [
    [40, 255, 140], [30, 220, 160], [60, 240, 120],
    [50, 200, 180], [80, 255, 100], [40, 230, 150],
  ],
}

const colors = PALETTES[props.palette] || PALETTES.aurora

// Aurora band definitions — right-side concentrated
const BANDS = [
  { cx: 0.65, w: 0.30, y: 0.08, h: 0.55, intensity: 1.0 },
  { cx: 0.72, w: 0.25, y: 0.05, h: 0.60, intensity: 0.8 },
  { cx: 0.58, w: 0.22, y: 0.12, h: 0.45, intensity: 0.7 },
  { cx: 0.78, w: 0.18, y: 0.10, h: 0.50, intensity: 0.5 },
  { cx: 0.50, w: 0.20, y: 0.15, h: 0.40, intensity: 0.4 },
]

function draw() {
  if (!ctx) return
  ctx.clearRect(0, 0, W, H)

  // Stars
  for (const s of stars) {
    const tw = 0.5 + 0.5 * Math.sin(t * s.freq + s.phase)
    const a = s.bright * tw
    if (a < 0.05) continue
    ctx.beginPath()
    ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(200,210,230,${a.toFixed(2)})`
    ctx.fill()
  }

  // Aurora bands — each is a vertical curtain with wavy horizontal structure
  for (let b = 0; b < BANDS.length; b++) {
    const band = BANDS[b]
    const col = colors[b % colors.length]
    const bandX = band.cx * W
    const bandW = band.w * W
    const bandY = band.y * H
    const bandH = band.h * H

    // Draw vertical strips (curtain columns)
    const cols = 40
    for (let i = 0; i < cols; i++) {
      const u = i / cols
      const x = bandX - bandW / 2 + u * bandW

      // Horizontal wave — each column shifts up/down
      const wave1 = 25 * Math.sin(u * 8 + t * 0.0012 + b * 1.7)
      const wave2 = 15 * Math.sin(u * 12 + t * 0.0018 + b * 2.3)
      const wave3 = 8 * Math.sin(u * 20 + t * 0.003 + b * 0.9)
      const yOff = wave1 + wave2 + wave3

      // Intensity varies along the band — brighter in center
      const centerDist = Math.abs(u - 0.5) * 2
      const hFade = 1 - centerDist * centerDist

      // Temporal shimmer — columns pulse independently
      const shimmer = 0.6 + 0.4 * Math.sin(t * 0.002 + u * 15 + b * 3.1)
      const pulse = 0.7 + 0.3 * Math.sin(t * 0.0008 + b * 2.7)

      const alpha = band.intensity * hFade * shimmer * pulse * 0.18
      if (alpha < 0.005) continue

      const colW = bandW / cols + 2
      const colH = bandH * (0.6 + hFade * 0.4)
      const colY = bandY + yOff

      // Vertical gradient per column — bright core fading top and bottom
      const grad = ctx.createLinearGradient(x, colY, x, colY + colH)
      grad.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},0)`)
      grad.addColorStop(0.15, `rgba(${col[0]},${col[1]},${col[2]},${(alpha * 0.3).toFixed(3)})`)
      grad.addColorStop(0.3, `rgba(${col[0]},${col[1]},${col[2]},${(alpha * 0.8).toFixed(3)})`)
      grad.addColorStop(0.5, `rgba(${col[0]},${col[1]},${col[2]},${alpha.toFixed(3)})`)
      grad.addColorStop(0.7, `rgba(${col[0]},${col[1]},${col[2]},${(alpha * 0.6).toFixed(3)})`)
      grad.addColorStop(0.9, `rgba(${col[0]},${col[1]},${col[2]},${(alpha * 0.15).toFixed(3)})`)
      grad.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`)

      ctx.fillStyle = grad
      ctx.fillRect(x, colY, colW, colH)
    }

    // Bright core line — the sharp edge at the top of the curtain
    ctx.beginPath()
    for (let i = 0; i <= cols; i++) {
      const u = i / cols
      const x = bandX - bandW / 2 + u * bandW
      const wave = 25 * Math.sin(u * 8 + t * 0.0012 + b * 1.7) + 15 * Math.sin(u * 12 + t * 0.0018 + b * 2.3)
      const y = bandY + wave + bandH * 0.28
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    const coreAlpha = band.intensity * 0.12 * (0.7 + 0.3 * Math.sin(t * 0.001 + b * 1.5))
    ctx.strokeStyle = `rgba(${Math.min(255, col[0] + 60)},${Math.min(255, col[1] + 40)},${Math.min(255, col[2] + 30)},${coreAlpha.toFixed(3)})`
    ctx.lineWidth = 2
    ctx.shadowBlur = 12
    ctx.shadowColor = `rgba(${col[0]},${col[1]},${col[2]},${(coreAlpha * 0.6).toFixed(3)})`
    ctx.stroke()
    ctx.shadowBlur = 0
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
