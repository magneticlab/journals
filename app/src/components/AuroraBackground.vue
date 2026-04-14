<template>
  <canvas ref="canvas" class="aurora-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({ palette: { type: String, default: 'midnight' } })
const canvas = ref(null)
let ctx, W = 0, H = 0, rafId, t = 0

// Stars
const STAR_COUNT = 90
let stars = []
function buildStars() {
  stars = Array.from({ length: STAR_COUNT }, () => ({
    x: Math.random(), y: Math.random() * 0.55,
    r: 0.3 + Math.random() * 0.8,
    freq: 0.0015 + Math.random() * 0.004,
    phase: Math.random() * Math.PI * 2,
    bright: 0.1 + Math.random() * 0.4,
  }))
}

const PALETTES = {
  midnight: [[50, 240, 160], [40, 200, 220], [80, 255, 130], [60, 180, 240]],
  dawn: [[240, 150, 60], [220, 120, 90], [255, 180, 40], [200, 140, 80]],
  daylight: [[50, 200, 210], [70, 220, 170], [40, 240, 190], [80, 180, 230]],
  dusk: [[150, 60, 230], [200, 40, 180], [120, 80, 255], [180, 50, 200]],
  aurora: [[30, 255, 150], [40, 220, 200], [60, 240, 120], [50, 200, 180]],
}
const colors = PALETTES[props.palette] || PALETTES.aurora

// Each curtain is a flowing bezier ribbon
const CURTAINS = [
  { col: 0, xBase: 0.55, width: 0.35, yTop: 0.04, yBot: 0.55, speed: 0.0006, waveAmp: 80, opacity: 0.16 },
  { col: 1, xBase: 0.65, width: 0.28, yTop: 0.06, yBot: 0.50, speed: 0.0008, waveAmp: 60, opacity: 0.12 },
  { col: 2, xBase: 0.48, width: 0.30, yTop: 0.08, yBot: 0.48, speed: 0.0005, waveAmp: 70, opacity: 0.10 },
  { col: 3, xBase: 0.72, width: 0.22, yTop: 0.03, yBot: 0.52, speed: 0.0007, waveAmp: 50, opacity: 0.08 },
]

function draw() {
  if (!ctx) return
  ctx.clearRect(0, 0, W, H)

  // Stars
  for (const s of stars) {
    const a = s.bright * (0.5 + 0.5 * Math.sin(t * s.freq + s.phase))
    if (a < 0.03) continue
    ctx.beginPath()
    ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(190,210,235,${a.toFixed(2)})`
    ctx.fill()
  }

  // Draw each curtain as layered soft ribbons
  for (const c of CURTAINS) {
    const [cr, cg, cb] = colors[c.col]
    const cx = c.xBase * W
    const halfW = c.width * W * 0.5

    // Multiple sub-layers per curtain for depth
    for (let layer = 0; layer < 6; layer++) {
      const layerU = layer / 5
      const layerShift = (layerU - 0.5) * halfW * 0.8
      const layerOpacity = c.opacity * (1 - Math.abs(layerU - 0.5) * 1.6)
      if (layerOpacity < 0.005) continue

      // Temporal shimmer per layer
      const shimmer = 0.6 + 0.4 * Math.sin(t * 0.0015 + layer * 1.8 + c.col * 2.1)
      const alpha = layerOpacity * shimmer

      // Build the curtain shape as a flowing path
      const segs = 24
      const points = []
      for (let i = 0; i <= segs; i++) {
        const v = i / segs
        const y = (c.yTop + v * (c.yBot - c.yTop)) * H

        // Flowing S-curve wave
        const wave1 = c.waveAmp * Math.sin(v * 3.5 + t * c.speed + layer * 0.7 + c.col)
        const wave2 = c.waveAmp * 0.5 * Math.sin(v * 5.2 + t * c.speed * 1.6 + layer * 1.2 + 2.4)
        const wave3 = c.waveAmp * 0.25 * Math.sin(v * 8 + t * c.speed * 2.4 + layer * 0.4 + 4.1)
        const x = cx + layerShift + wave1 + wave2 + wave3

        // Width tapers: thin at top, wider in middle, thin at bottom
        const taper = Math.sin(v * Math.PI) * 0.8 + 0.2
        const ribbonW = 8 + taper * 25

        points.push({ x, y, w: ribbonW })
      }

      // Draw as a filled ribbon with soft edges
      ctx.beginPath()
      // Left edge
      for (let i = 0; i < points.length; i++) {
        const p = points[i]
        const x = p.x - p.w
        i === 0 ? ctx.moveTo(x, p.y) : ctx.lineTo(x, p.y)
      }
      // Right edge (reverse)
      for (let i = points.length - 1; i >= 0; i--) {
        const p = points[i]
        ctx.lineTo(p.x + p.w, p.y)
      }
      ctx.closePath()

      // Vertical gradient
      const yStart = c.yTop * H
      const yEnd = c.yBot * H
      const grad = ctx.createLinearGradient(0, yStart, 0, yEnd)
      grad.addColorStop(0, `rgba(${cr},${cg},${cb},0)`)
      grad.addColorStop(0.12, `rgba(${cr},${cg},${cb},${(alpha * 0.4).toFixed(3)})`)
      grad.addColorStop(0.3, `rgba(${cr},${cg},${cb},${(alpha * 0.9).toFixed(3)})`)
      grad.addColorStop(0.5, `rgba(${cr},${cg},${cb},${alpha.toFixed(3)})`)
      grad.addColorStop(0.75, `rgba(${cr},${cg},${cb},${(alpha * 0.5).toFixed(3)})`)
      grad.addColorStop(1, `rgba(${cr},${cg},${cb},0)`)

      ctx.filter = 'blur(6px)'
      ctx.fillStyle = grad
      ctx.fill()
      ctx.filter = 'none'
    }

    // Bright inner fold — the sharp bright edge
    const foldSegs = 30
    ctx.beginPath()
    for (let i = 0; i <= foldSegs; i++) {
      const v = i / foldSegs
      const y = (c.yTop + v * (c.yBot - c.yTop)) * H
      const wave = c.waveAmp * Math.sin(v * 3.5 + t * c.speed + c.col)
        + c.waveAmp * 0.5 * Math.sin(v * 5.2 + t * c.speed * 1.6 + 2.4)
      const x = cx + wave
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    const foldPulse = 0.5 + 0.5 * Math.sin(t * 0.001 + c.col * 2)
    const foldAlpha = c.opacity * 0.7 * foldPulse
    ctx.strokeStyle = `rgba(${Math.min(255, cr + 80)},${Math.min(255, cg + 60)},${Math.min(255, cb + 40)},${foldAlpha.toFixed(3)})`
    ctx.lineWidth = 1.5
    ctx.filter = 'blur(3px)'
    ctx.stroke()
    ctx.filter = 'none'
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
