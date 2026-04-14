<template>
  <canvas ref="canvas" class="diag-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({ palette: { type: String, default: 'midnight' } })

const canvas = ref(null)
let ctx, W = 0, H = 0, t = 0, rafId

const TILT = 1.62
const FOCAL_X = 0.66
const FOCAL_Y = 0.50
const SPACING = 28

const PALETTES = {
  midnight: [
    { rgb: [120,80,255], speed: 1.00, freq: 0.0082, A: 22, th: 72, op: 0.20 },
    { rgb: [160,110,255], speed: -0.88, freq: 0.0090, A: 20, th: 68, op: 0.18 },
    { rgb: [100,190,255], speed: 0.96, freq: 0.0078, A: 24, th: 72, op: 0.19 },
    { rgb: [165,180,252], speed: -1.05, freq: 0.0086, A: 19, th: 66, op: 0.17 },
    { rgb: [255,100,130], speed: 0.84, freq: 0.0094, A: 23, th: 70, op: 0.19 },
    { rgb: [255,140,80], speed: -0.98, freq: 0.0080, A: 20, th: 68, op: 0.18 },
    { rgb: [255,180,60], speed: 1.08, freq: 0.0088, A: 22, th: 72, op: 0.18 },
    { rgb: [200,220,60], speed: -0.86, freq: 0.0076, A: 21, th: 68, op: 0.17 },
    { rgb: [80,220,140], speed: 0.93, freq: 0.0092, A: 20, th: 66, op: 0.17 },
    { rgb: [52,211,180], speed: -1.02, freq: 0.0084, A: 23, th: 70, op: 0.16 },
  ],
  dawn: [
    { rgb: [230,140,60], speed: 1.00, freq: 0.0082, A: 22, th: 72, op: 0.20 },
    { rgb: [240,120,80], speed: -0.88, freq: 0.0090, A: 20, th: 68, op: 0.18 },
    { rgb: [220,100,100], speed: 0.96, freq: 0.0078, A: 24, th: 72, op: 0.19 },
    { rgb: [200,130,80], speed: -1.05, freq: 0.0086, A: 19, th: 66, op: 0.17 },
    { rgb: [240,160,50], speed: 0.84, freq: 0.0094, A: 23, th: 70, op: 0.19 },
    { rgb: [220,180,70], speed: -0.98, freq: 0.0080, A: 20, th: 68, op: 0.18 },
    { rgb: [180,160,100], speed: 1.08, freq: 0.0088, A: 22, th: 72, op: 0.18 },
    { rgb: [160,130,120], speed: -0.86, freq: 0.0076, A: 21, th: 68, op: 0.17 },
    { rgb: [200,150,90], speed: 0.93, freq: 0.0092, A: 20, th: 66, op: 0.17 },
    { rgb: [230,170,60], speed: -1.02, freq: 0.0084, A: 23, th: 70, op: 0.16 },
  ],
  daylight: [
    { rgb: [90,150,255], speed: 1.00, freq: 0.0082, A: 22, th: 72, op: 0.18 },
    { rgb: [100,180,240], speed: -0.88, freq: 0.0090, A: 20, th: 68, op: 0.16 },
    { rgb: [70,200,200], speed: 0.96, freq: 0.0078, A: 24, th: 72, op: 0.17 },
    { rgb: [80,210,160], speed: -1.05, freq: 0.0086, A: 19, th: 66, op: 0.15 },
    { rgb: [120,190,130], speed: 0.84, freq: 0.0094, A: 23, th: 70, op: 0.17 },
    { rgb: [160,200,100], speed: -0.98, freq: 0.0080, A: 20, th: 68, op: 0.16 },
    { rgb: [100,170,220], speed: 1.08, freq: 0.0088, A: 22, th: 72, op: 0.16 },
    { rgb: [80,160,240], speed: -0.86, freq: 0.0076, A: 21, th: 68, op: 0.15 },
    { rgb: [110,140,255], speed: 0.93, freq: 0.0092, A: 20, th: 66, op: 0.15 },
    { rgb: [70,190,180], speed: -1.02, freq: 0.0084, A: 23, th: 70, op: 0.14 },
  ],
  dusk: [
    { rgb: [140,80,200], speed: 1.00, freq: 0.0082, A: 22, th: 72, op: 0.20 },
    { rgb: [180,60,180], speed: -0.88, freq: 0.0090, A: 20, th: 68, op: 0.18 },
    { rgb: [200,50,140], speed: 0.96, freq: 0.0078, A: 24, th: 72, op: 0.19 },
    { rgb: [220,70,100], speed: -1.05, freq: 0.0086, A: 19, th: 66, op: 0.17 },
    { rgb: [200,90,80], speed: 0.84, freq: 0.0094, A: 23, th: 70, op: 0.19 },
    { rgb: [180,100,120], speed: -0.98, freq: 0.0080, A: 20, th: 68, op: 0.18 },
    { rgb: [160,80,160], speed: 1.08, freq: 0.0088, A: 22, th: 72, op: 0.18 },
    { rgb: [120,70,200], speed: -0.86, freq: 0.0076, A: 21, th: 68, op: 0.17 },
    { rgb: [100,90,220], speed: 0.93, freq: 0.0092, A: 20, th: 66, op: 0.17 },
    { rgb: [140,60,190], speed: -1.02, freq: 0.0084, A: 23, th: 70, op: 0.16 },
  ],
  aurora: [
    { rgb: [40,120,200], speed: 1.00, freq: 0.0082, A: 22, th: 72, op: 0.20 },
    { rgb: [60,80,220], speed: -0.88, freq: 0.0090, A: 20, th: 68, op: 0.18 },
    { rgb: [50,160,180], speed: 0.96, freq: 0.0078, A: 24, th: 72, op: 0.19 },
    { rgb: [40,200,160], speed: -1.05, freq: 0.0086, A: 19, th: 66, op: 0.17 },
    { rgb: [70,140,220], speed: 0.84, freq: 0.0094, A: 23, th: 70, op: 0.19 },
    { rgb: [100,80,240], speed: -0.98, freq: 0.0080, A: 20, th: 68, op: 0.18 },
    { rgb: [70,100,180], speed: 1.08, freq: 0.0088, A: 22, th: 72, op: 0.18 },
    { rgb: [40,170,200], speed: -0.86, freq: 0.0076, A: 21, th: 68, op: 0.17 },
    { rgb: [80,60,190], speed: 0.93, freq: 0.0092, A: 20, th: 66, op: 0.17 },
    { rgb: [40,120,200], speed: -1.02, freq: 0.0084, A: 23, th: 70, op: 0.16 },
  ],
}

const RIBBONS = PALETTES[props.palette] || PALETTES.midnight

function draw() {
  if (!ctx) return
  ctx.clearRect(0, 0, W, H)
  const focalX = W * FOCAL_X, focalY = H * FOCAL_Y
  const baseCy = focalY - focalX * TILT
  const gradSpan = (W * TILT + H) * 0.9

  for (let i = 0; i < RIBBONS.length; i++) {
    const r = RIBBONS[i]
    const cyPx = baseCy + (i - 4.5) * SPACING
    const half = r.th / 2
    const phase = t * r.speed * 0.0055

    ctx.beginPath()
    const step = 3
    for (let x = -step; x <= W + step; x += step) {
      const y = cyPx + x * TILT + r.A * Math.sin(x * r.freq + phase)
      x <= 0 ? ctx.moveTo(x, y - half) : ctx.lineTo(x, y - half)
    }
    for (let x = W + step; x >= -step; x -= step) {
      const y = cyPx + x * TILT + r.A * Math.sin(x * r.freq + phase)
      ctx.lineTo(x, y + half)
    }
    ctx.closePath()

    const [rv, gv, bv] = r.rgb
    const c = (a) => `rgba(${rv},${gv},${bv},${a.toFixed(3)})`
    const grad = ctx.createLinearGradient(0, focalY - gradSpan, 0, focalY + gradSpan)
    grad.addColorStop(0, c(0))
    grad.addColorStop(0.30, c(0))
    grad.addColorStop(0.40, c(r.op * 0.5))
    grad.addColorStop(0.50, c(r.op))
    grad.addColorStop(0.60, c(r.op * 0.5))
    grad.addColorStop(0.70, c(0))
    grad.addColorStop(1, c(0))
    ctx.fillStyle = grad
    ctx.fill()
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
}

onMounted(() => { resize(); window.addEventListener('resize', resize); draw() })
onUnmounted(() => { window.removeEventListener('resize', resize); cancelAnimationFrame(rafId) })
</script>

<style scoped>
.diag-canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; }
</style>
