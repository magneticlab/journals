<template>
  <canvas ref="canvas" class="ribbon-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
let ctx, W, H, t = 0, rafId

// Tuned for dark theme — bleeding from top, muted complementary colors
const TILT = 0.45
const FOCAL_X = 0.50
const FOCAL_Y = 0.12  // top area — bleeds from above
const SPACING = 10
const N = 48
const HALF = (N - 1) / 2

// Dark-theme palette — muted, complementary to our blue/green/purple brand
const PALETTE = [
  [99, 149, 255],   // brand blue
  [120, 160, 255],  // bright blue
  [80, 180, 240],   // sky
  [52, 211, 180],   // teal
  [52, 211, 153],   // brand green
  [80, 200, 130],   // emerald
  [167, 139, 250],  // brand purple
  [140, 120, 230],  // violet
  [180, 130, 255],  // lavender
  [100, 170, 255],  // cornflower
  [60, 195, 200],   // cyan
  [99, 149, 255],   // brand blue loop
]

function lerpColor(u) {
  const scaled = u * (PALETTE.length - 1)
  const lo = Math.floor(scaled)
  const hi = Math.min(lo + 1, PALETTE.length - 1)
  const f = scaled - lo
  const a = PALETTE[lo], b = PALETTE[hi]
  return [
    Math.round(a[0] + (b[0] - a[0]) * f),
    Math.round(a[1] + (b[1] - a[1]) * f),
    Math.round(a[2] + (b[2] - a[2]) * f),
  ]
}

const RIBBONS = Array.from({ length: N }, (_, i) => {
  const distFromCenter = Math.abs(i - HALF) / HALF
  const centerFactor = Math.pow(1 - distFromCenter, 1.6)
  return {
    rgb: lerpColor(i / (N - 1)),
    speed: (i % 2 === 0 ? 1 : -1) * (0.6 + (i % 7) * 0.03),
    freq: 0.005 + (i % 5) * 0.0003,
    A: 20 + (i % 3) * 3,
    th: 32 + (i % 2) * 6,
    op: 0.05 + centerFactor * 0.18,  // slightly more vibrant — max ~0.23
  }
})

const MAX_BLUR = 12
const EDGE_COUNT = 6

function ribbonBlur(index) {
  const fromEdge = Math.min(index, N - 1 - index)
  if (fromEdge >= EDGE_COUNT) return 0
  const u = 1 - fromEdge / EDGE_COUNT
  return Math.pow(u, 1.8) * MAX_BLUR
}

const BUNDLE_AMP = 60
const BUNDLE_CURVE_FREQ = (Math.PI * 0.6) / 1440
const BUNDLE_CURVE_SPD = 0.00015

const COIL_FREQ = (Math.PI * 1.2) / 1440
const COIL_SPD = 0.00025

function draw() {
  if (!ctx) return
  ctx.clearRect(0, 0, W, H)

  const focalX = W * FOCAL_X
  const focalY = H * FOCAL_Y
  const baseCy = focalY - focalX * TILT
  const gradSpan = (W * TILT + H) * 0.9

  const TWIST_AMP = SPACING * 1.8
  const twistFreq = (Math.PI * 0.7) / W

  for (let i = 0; i < N; i++) {
    const r = RIBBONS[i]
    const ribbonOffset = (i - HALF) * SPACING
    const half = r.th / 2
    const animPhase = t * r.speed * 0.003
    const ribbonAngle = (i / N) * Math.PI * 2
    const blur = ribbonBlur(i)

    ctx.filter = blur > 0.4 ? `blur(${blur.toFixed(1)}px)` : 'none'
    ctx.shadowBlur = 0
    ctx.shadowColor = 'transparent'

    ctx.beginPath()
    const step = 6
    for (let x = -step; x <= W + step; x += step) {
      const bundleCurve = BUNDLE_AMP * Math.sin(x * BUNDLE_CURVE_FREQ + t * BUNDLE_CURVE_SPD)
      const coilFactor = Math.sin(x * COIL_FREQ + t * COIL_SPD)
      const twist = TWIST_AMP * Math.sin(x * twistFreq + ribbonAngle)
      const y = baseCy + ribbonOffset * coilFactor + x * TILT
                + bundleCurve + r.A * Math.sin(x * r.freq + animPhase) + twist
      x <= 0 ? ctx.moveTo(x, y - half) : ctx.lineTo(x, y - half)
    }
    for (let x = W + step; x >= -step; x -= step) {
      const bundleCurve = BUNDLE_AMP * Math.sin(x * BUNDLE_CURVE_FREQ + t * BUNDLE_CURVE_SPD)
      const coilFactor = Math.sin(x * COIL_FREQ + t * COIL_SPD)
      const twist = TWIST_AMP * Math.sin(x * twistFreq + ribbonAngle)
      const y = baseCy + ribbonOffset * coilFactor + x * TILT
                + bundleCurve + r.A * Math.sin(x * r.freq + animPhase) + twist
      ctx.lineTo(x, y + half)
    }
    ctx.closePath()

    const [rv, gv, bv] = r.rgb
    const c = (a) => `rgba(${rv},${gv},${bv},${a.toFixed(3)})`

    // Gradient fades from top (visible) to bottom (invisible)
    const grad = ctx.createLinearGradient(0, 0, 0, H)
    grad.addColorStop(0, c(r.op * 0.6))
    grad.addColorStop(0.15, c(r.op))
    grad.addColorStop(0.35, c(r.op * 0.7))
    grad.addColorStop(0.55, c(r.op * 0.2))
    grad.addColorStop(0.75, c(0))
    grad.addColorStop(1, c(0))

    ctx.fillStyle = grad
    ctx.fill()
  }

  ctx.filter = 'none'
  ctx.shadowBlur = 0
  ctx.shadowColor = 'transparent'
  t++
  rafId = requestAnimationFrame(draw)
}

function resize() {
  if (!canvas.value) return
  const dpr = window.devicePixelRatio || 1
  W = canvas.value.offsetWidth
  H = canvas.value.offsetHeight
  canvas.value.width = W * dpr
  canvas.value.height = H * dpr
  ctx = canvas.value.getContext('2d')
  ctx.scale(dpr, dpr)
}

onMounted(() => {
  resize()
  window.addEventListener('resize', resize)
  draw()
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  cancelAnimationFrame(rafId)
})
</script>

<style scoped>
.ribbon-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 0;
}
</style>
