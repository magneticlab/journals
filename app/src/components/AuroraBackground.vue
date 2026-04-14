<template>
  <div class="aurora-wrap">
    <canvas ref="glowCanvas" class="aurora-layer" />
    <canvas ref="mainCanvas" class="aurora-layer" />
    <canvas ref="starCanvas" class="aurora-layer" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { createNoise3D } from 'simplex-noise'

const props = defineProps({ palette: { type: String, default: 'midnight' } })
const mainCanvas = ref(null)
const glowCanvas = ref(null)
const starCanvas = ref(null)
let mainCtx, glowCtx, starCtx
let W = 0, H = 0, rafId, t = 0
const noise = createNoise3D()

// Stars — drawn once, only redraw on resize
const STAR_COUNT = 100
function drawStars() {
  if (!starCtx) return
  starCtx.clearRect(0, 0, W, H)
  for (let i = 0; i < STAR_COUNT; i++) {
    const x = Math.random() * W
    const y = Math.random() * H * 0.5
    const r = 0.3 + Math.random() * 0.9
    const a = 0.1 + Math.random() * 0.35
    starCtx.beginPath()
    starCtx.arc(x, y, r, 0, Math.PI * 2)
    starCtx.fillStyle = `rgba(200,215,240,${a})`
    starCtx.fill()
  }
}

// Color palettes — aurora curtain colors
const PALETTES = {
  midnight: [
    [[30, 255, 140], [40, 220, 180], [60, 200, 240], [120, 80, 220]],
    [[50, 240, 160], [30, 200, 200], [80, 160, 255], [140, 60, 240]],
    [[40, 255, 120], [60, 230, 170], [50, 180, 220], [100, 100, 255]],
  ],
  dawn: [
    [[240, 160, 50], [220, 120, 80], [200, 100, 120], [180, 80, 140]],
    [[255, 180, 40], [230, 140, 70], [210, 110, 100], [190, 90, 130]],
    [[230, 150, 60], [210, 130, 90], [190, 110, 110], [170, 90, 150]],
  ],
  daylight: [
    [[50, 210, 200], [60, 230, 170], [80, 200, 240], [100, 160, 255]],
    [[40, 220, 190], [70, 240, 160], [60, 190, 230], [90, 170, 250]],
    [[60, 200, 210], [50, 220, 180], [70, 210, 240], [110, 150, 240]],
  ],
  dusk: [
    [[140, 60, 230], [180, 40, 200], [200, 50, 160], [160, 70, 250]],
    [[120, 80, 240], [160, 50, 220], [190, 60, 180], [140, 90, 255]],
    [[150, 50, 220], [170, 60, 200], [210, 40, 170], [130, 80, 250]],
  ],
  aurora: [
    [[20, 255, 130], [30, 230, 180], [50, 200, 230], [80, 120, 255]],
    [[40, 250, 150], [25, 220, 200], [60, 180, 240], [100, 80, 240]],
    [[30, 240, 140], [45, 210, 190], [40, 200, 220], [90, 100, 250]],
  ],
}

const curtainColors = PALETTES[props.palette] || PALETTES.aurora

// Curtain definitions
const CURTAINS = [
  { xCenter: 0.58, spread: 0.22, yStart: 0.02, yEnd: 0.58, noiseSeed: 0, speed: 1.0, opacity: 1.0 },
  { xCenter: 0.68, spread: 0.18, yStart: 0.04, yEnd: 0.52, noiseSeed: 100, speed: 0.8, opacity: 0.8 },
  { xCenter: 0.48, spread: 0.20, yStart: 0.06, yEnd: 0.50, noiseSeed: 200, speed: 1.2, opacity: 0.6 },
]

function drawCurtain(ctx, curtain, colorSet, time) {
  const segs = 48
  const cx = curtain.xCenter * W
  const spread = curtain.spread * W

  // Build curtain shape points using noise
  const leftPts = []
  const rightPts = []
  const midPts = []

  for (let i = 0; i <= segs; i++) {
    const v = i / segs
    const y = (curtain.yStart + v * (curtain.yEnd - curtain.yStart)) * H

    // Slow drift — large-scale curtain shape
    const drift = noise(
      v * 1.5 + curtain.noiseSeed,
      time * 0.00015 * curtain.speed,
      curtain.noiseSeed * 0.1
    ) * spread * 1.8

    // Fast shimmer — fine vertical ripple
    const shimmer = noise(
      v * 8 + curtain.noiseSeed,
      time * 0.0015 * curtain.speed,
      curtain.noiseSeed * 0.3 + 50
    ) * spread * 0.25

    // Medium wave
    const wave = noise(
      v * 3 + curtain.noiseSeed + 30,
      time * 0.0004 * curtain.speed,
      curtain.noiseSeed * 0.2 + 20
    ) * spread * 0.7

    const xMid = cx + drift + wave + shimmer

    // Width tapers at top and bottom, wider in the belly
    const taper = Math.pow(Math.sin(v * Math.PI), 0.6)
    const widthNoise = noise(v * 4 + curtain.noiseSeed + 60, time * 0.0003, 0) * 0.3 + 0.7
    const halfW = spread * 0.3 * taper * widthNoise

    leftPts.push({ x: xMid - halfW, y })
    rightPts.push({ x: xMid + halfW, y })
    midPts.push({ x: xMid, y })
  }

  // Fill the curtain shape
  ctx.beginPath()
  ctx.moveTo(leftPts[0].x, leftPts[0].y)
  for (let i = 1; i < leftPts.length; i++) {
    const prev = leftPts[i - 1], curr = leftPts[i]
    ctx.quadraticCurveTo(prev.x, prev.y, (prev.x + curr.x) / 2, (prev.y + curr.y) / 2)
  }
  ctx.lineTo(leftPts[leftPts.length - 1].x, leftPts[leftPts.length - 1].y)
  for (let i = rightPts.length - 1; i >= 0; i--) {
    const curr = rightPts[i]
    const next = i > 0 ? rightPts[i - 1] : rightPts[0]
    ctx.quadraticCurveTo(curr.x, curr.y, (curr.x + next.x) / 2, (curr.y + next.y) / 2)
  }
  ctx.closePath()

  // Vertical color gradient
  const grad = ctx.createLinearGradient(0, curtain.yStart * H, 0, curtain.yEnd * H)
  const [c0, c1, c2, c3] = colorSet
  const baseAlpha = 0.14 * curtain.opacity
  grad.addColorStop(0, `rgba(${c3[0]},${c3[1]},${c3[2]},0)`)
  grad.addColorStop(0.15, `rgba(${c3[0]},${c3[1]},${c3[2]},${baseAlpha * 0.3})`)
  grad.addColorStop(0.3, `rgba(${c2[0]},${c2[1]},${c2[2]},${baseAlpha * 0.7})`)
  grad.addColorStop(0.45, `rgba(${c1[0]},${c1[1]},${c1[2]},${baseAlpha})`)
  grad.addColorStop(0.6, `rgba(${c0[0]},${c0[1]},${c0[2]},${baseAlpha * 0.9})`)
  grad.addColorStop(0.8, `rgba(${c0[0]},${c0[1]},${c0[2]},${baseAlpha * 0.4})`)
  grad.addColorStop(1, `rgba(${c0[0]},${c0[1]},${c0[2]},0)`)

  ctx.fillStyle = grad
  ctx.fill()

  // Bright fold line along the center
  ctx.beginPath()
  ctx.moveTo(midPts[0].x, midPts[0].y)
  for (let i = 1; i < midPts.length; i++) {
    const prev = midPts[i - 1], curr = midPts[i]
    ctx.quadraticCurveTo(prev.x, prev.y, (prev.x + curr.x) / 2, (prev.y + curr.y) / 2)
  }
  const foldPulse = 0.5 + 0.5 * noise(time * 0.0003, curtain.noiseSeed, 0)
  const foldAlpha = 0.08 * curtain.opacity * foldPulse
  ctx.strokeStyle = `rgba(${Math.min(255, c0[0] + 100)},${Math.min(255, c0[1] + 80)},${Math.min(255, c0[2] + 60)},${foldAlpha})`
  ctx.lineWidth = 2
  ctx.stroke()
}

function draw() {
  if (!mainCtx || !glowCtx) { rafId = requestAnimationFrame(draw); return }

  // Clear main
  mainCtx.clearRect(0, 0, W, H)

  // Draw curtains to main canvas
  mainCtx.globalCompositeOperation = 'screen'
  for (let c = 0; c < CURTAINS.length; c++) {
    drawCurtain(mainCtx, CURTAINS[c], curtainColors[c % curtainColors.length], t)
  }
  mainCtx.globalCompositeOperation = 'source-over'

  // Glow pass — blur the main canvas content onto glow canvas
  glowCtx.clearRect(0, 0, W, H)
  glowCtx.filter = 'blur(40px)'
  glowCtx.globalAlpha = 0.5
  glowCtx.drawImage(mainCanvas.value, 0, 0)
  glowCtx.globalAlpha = 1
  glowCtx.filter = 'none'

  // Second wide glow pass
  glowCtx.filter = 'blur(80px)'
  glowCtx.globalAlpha = 0.25
  glowCtx.drawImage(mainCanvas.value, 0, 0)
  glowCtx.globalAlpha = 1
  glowCtx.filter = 'none'

  // Twinkle some stars
  if (starCtx && t % 3 === 0) {
    starCtx.clearRect(0, 0, W, H)
    for (let i = 0; i < STAR_COUNT; i++) {
      // Deterministic position from index
      const seed = i * 7919
      const x = ((seed * 13) % 10000) / 10000 * W
      const y = ((seed * 17) % 10000) / 10000 * H * 0.5
      const r = 0.3 + ((seed * 23) % 100) / 100 * 0.9
      const twinkle = 0.5 + 0.5 * Math.sin(t * (0.002 + (seed % 100) * 0.00004) + seed)
      const a = (0.08 + ((seed * 31) % 100) / 100 * 0.3) * twinkle
      if (a < 0.02) continue
      starCtx.beginPath()
      starCtx.arc(x, y, r, 0, Math.PI * 2)
      starCtx.fillStyle = `rgba(200,215,240,${a.toFixed(2)})`
      starCtx.fill()
    }
  }

  t++
  rafId = requestAnimationFrame(draw)
}

function resize() {
  const dpr = window.devicePixelRatio || 1
  for (const c of [mainCanvas.value, glowCanvas.value, starCanvas.value]) {
    if (!c) continue
    W = c.offsetWidth; H = c.offsetHeight
    c.width = W * dpr; c.height = H * dpr
    const cx = c.getContext('2d')
    cx.scale(dpr, dpr)
  }
  mainCtx = mainCanvas.value?.getContext('2d')
  glowCtx = glowCanvas.value?.getContext('2d')
  starCtx = starCanvas.value?.getContext('2d')
}

onMounted(() => { resize(); window.addEventListener('resize', resize); draw() })
onUnmounted(() => { window.removeEventListener('resize', resize); cancelAnimationFrame(rafId) })
</script>

<style scoped>
.aurora-wrap { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; }
.aurora-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
</style>
