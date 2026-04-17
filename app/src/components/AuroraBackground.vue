<template>
  <div class="aurora-wrap">
    <canvas ref="canvas" class="aurora-canvas" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { createNoise3D } from 'simplex-noise'

const props = defineProps({ palette: { type: String, default: 'midnight' } })
const canvas = ref(null)
let ctx, W = 0, H = 0, rafId, t = 0
const noise = createNoise3D()

const PALETTES = {
  midnight: [
    [[30, 255, 120], [40, 240, 180], [60, 200, 240], [140, 100, 255], [200, 60, 220], [255, 80, 160]],
    [[255, 80, 160], [200, 60, 240], [120, 80, 255], [60, 160, 240], [40, 220, 200], [80, 255, 140]],
    [[40, 220, 200], [80, 180, 255], [140, 120, 240], [60, 240, 160], [100, 200, 230], [50, 255, 180]],
  ],
  dawn: [
    [[255, 220, 60], [255, 180, 50], [240, 140, 70], [220, 100, 100], [200, 80, 140], [180, 60, 160]],
    [[255, 140, 80], [240, 110, 100], [220, 80, 130], [200, 100, 160], [230, 160, 60], [255, 200, 40]],
    [[240, 170, 50], [220, 130, 80], [200, 100, 110], [230, 150, 60], [250, 190, 40], [240, 160, 70]],
  ],
  daylight: [
    [[60, 240, 160], [50, 220, 200], [70, 200, 240], [100, 160, 255], [80, 240, 140], [60, 250, 180]],
    [[80, 220, 200], [60, 200, 240], [90, 170, 255], [50, 240, 180], [70, 230, 160], [100, 200, 220]],
    [[50, 250, 160], [60, 230, 190], [80, 200, 230], [70, 240, 170], [90, 210, 200], [60, 250, 150]],
  ],
  dusk: [
    [[140, 60, 255], [180, 50, 230], [220, 50, 180], [255, 60, 140], [200, 70, 240], [160, 80, 255]],
    [[255, 50, 140], [220, 60, 180], [180, 70, 230], [140, 80, 255], [200, 50, 200], [240, 60, 160]],
    [[120, 80, 250], [160, 60, 230], [200, 50, 200], [180, 70, 240], [140, 90, 255], [170, 50, 220]],
  ],
  aurora: [
    [[20, 255, 120], [30, 240, 170], [50, 200, 230], [80, 140, 255], [40, 255, 160], [60, 230, 200]],
    [[50, 240, 180], [30, 220, 220], [60, 180, 250], [80, 120, 255], [40, 250, 190], [50, 230, 210]],
    [[30, 250, 150], [40, 230, 190], [60, 200, 230], [50, 255, 170], [70, 220, 200], [40, 240, 180]],
  ],
}
const colorSets = PALETTES[props.palette] || PALETTES.aurora

// Stars
const STAR_COUNT = 70
function drawStars() {
  for (let i = 0; i < STAR_COUNT; i++) {
    const seed = i * 7919
    const x = ((seed * 13) % 10000) / 10000 * W
    const y = ((seed * 17) % 10000) / 10000 * H * 0.35
    const r = 0.3 + ((seed * 23) % 100) / 100 * 0.6
    const tw = 0.5 + 0.5 * Math.sin(t * (0.002 + (seed % 50) * 0.00003) + seed)
    const a = (0.04 + ((seed * 31) % 100) / 100 * 0.15) * tw
    if (a < 0.015) continue
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(200,215,240,${a.toFixed(2)})`; ctx.fill()
  }
}

// 3 flowing ribbon bands — wide, soft, like paint in water
const RIBBONS = [
  { seed: 0, speed: 1.0, width: 0.12, yBase: 0.22, opacity: 0.22, colSet: 0 },
  { seed: 100, speed: 0.7, width: 0.08, yBase: 0.18, opacity: 0.14, colSet: 1 },
  { seed: 200, speed: 1.2, width: 0.06, yBase: 0.26, opacity: 0.10, colSet: 2 },
]

function drawRibbon(ribbon) {
  const cs = colorSets[ribbon.colSet % colorSets.length]
  const pts = 80 // resolution along the ribbon
  const yCenter = ribbon.yBase * H

  // Build the flowing center line
  const centerLine = []
  for (let i = 0; i <= pts; i++) {
    const u = i / pts
    const x = u * W * 1.2 - W * 0.1 // extend slightly beyond viewport

    // Smooth flowing displacement — like silk in water
    const flow1 = noise(u * 1.5 + ribbon.seed, t * 0.00008 * ribbon.speed, 0) * H * 0.15
    const flow2 = noise(u * 3.5 + ribbon.seed + 40, t * 0.00018 * ribbon.speed, 10) * H * 0.06
    const flow3 = noise(u * 7 + ribbon.seed + 80, t * 0.0005 * ribbon.speed, 20) * H * 0.02

    const y = yCenter + flow1 + flow2 + flow3

    // Width breathes with noise — creates the dissolving paint effect
    const widthMod = 0.5 + 0.5 * noise(u * 2 + ribbon.seed + 60, t * 0.00012 * ribbon.speed, 30)
    const w = ribbon.width * H * widthMod

    // Edge softness — occasionally one edge expands outward (dissolves)
    const edgeNoise = noise(u * 3 + ribbon.seed + 90, t * 0.0003 * ribbon.speed, 60)
    const topSoft = edgeNoise > 0.2 ? (edgeNoise - 0.2) * w * 1.5 : 0
    const botSoft = edgeNoise < -0.2 ? (-edgeNoise - 0.2) * w * 1.5 : 0

    centerLine.push({ x, y, w, topSoft, botSoft })
  }

  // Draw as a filled shape with smooth curves
  ctx.beginPath()

  // Top edge
  ctx.moveTo(centerLine[0].x, centerLine[0].y - centerLine[0].w)
  for (let i = 1; i < centerLine.length; i++) {
    const prev = centerLine[i - 1], curr = centerLine[i]
    const py = prev.y - prev.w, cy = curr.y - curr.w
    ctx.quadraticCurveTo(prev.x, py, (prev.x + curr.x) / 2, (py + cy) / 2)
  }

  // Bottom edge (reverse)
  for (let i = centerLine.length - 1; i >= 0; i--) {
    const curr = centerLine[i]
    const prev = i > 0 ? centerLine[i - 1] : centerLine[0]
    const cy = curr.y + curr.w, py = prev.y + prev.w
    ctx.quadraticCurveTo(curr.x, cy, (curr.x + prev.x) / 2, (cy + py) / 2)
  }
  ctx.closePath()

  // Horizontal gradient — full spectrum across the ribbon
  const grad = ctx.createLinearGradient(0, 0, W, 0)
  const a = ribbon.opacity

  // Smooth color cycling — interpolate between colors, no hard jumps
  const shift = (t * 0.00003 * ribbon.speed) % cs.length

  function getShiftedColor(ci) {
    const idx = (ci + shift) % cs.length
    const lo = Math.floor(idx) % cs.length
    const hi = (lo + 1) % cs.length
    const f = idx - Math.floor(idx)
    return [
      Math.round(cs[lo][0] + (cs[hi][0] - cs[lo][0]) * f),
      Math.round(cs[lo][1] + (cs[hi][1] - cs[lo][1]) * f),
      Math.round(cs[lo][2] + (cs[hi][2] - cs[lo][2]) * f),
    ]
  }

  const gc0 = getShiftedColor(0), gc1 = getShiftedColor(1), gc2 = getShiftedColor(2)
  const gc3 = getShiftedColor(3), gc4 = getShiftedColor(4), gc5 = getShiftedColor(5)

  grad.addColorStop(0, `rgba(${gc0[0]},${gc0[1]},${gc0[2]},0)`)
  grad.addColorStop(0.10, `rgba(${gc0[0]},${gc0[1]},${gc0[2]},${(a * 0.4).toFixed(3)})`)
  grad.addColorStop(0.25, `rgba(${gc1[0]},${gc1[1]},${gc1[2]},${(a * 0.8).toFixed(3)})`)
  grad.addColorStop(0.40, `rgba(${gc2[0]},${gc2[1]},${gc2[2]},${a.toFixed(3)})`)
  grad.addColorStop(0.55, `rgba(${gc3[0]},${gc3[1]},${gc3[2]},${a.toFixed(3)})`)
  grad.addColorStop(0.70, `rgba(${gc4[0]},${gc4[1]},${gc4[2]},${(a * 0.7).toFixed(3)})`)
  grad.addColorStop(0.85, `rgba(${gc5[0]},${gc5[1]},${gc5[2]},${(a * 0.3).toFixed(3)})`)
  grad.addColorStop(1, `rgba(${gc5[0]},${gc5[1]},${gc5[2]},0)`)

  ctx.fillStyle = grad
  ctx.fill()

  // Traveling blur on edges — soft dissolution zones that sweep along
  // Draw the bottom edge as a separate thick stroke with varying opacity
  // A "focus point" travels left-to-right, blurring what's behind it
  const blurSpeed1 = 0.00006 * ribbon.speed
  const blurSpeed2 = 0.00009 * ribbon.speed
  // Two focus waves traveling in opposite directions
  const focus1 = (Math.sin(t * blurSpeed1 + ribbon.seed) + 1) / 2 // 0-1, sweeps right
  const focus2 = (Math.sin(t * blurSpeed2 + ribbon.seed + 3) + 1) / 2 // offset, sweeps left

  // Bottom edge blur strokes
  for (let pass = 0; pass < 4; pass++) {
    const spread = (pass + 1) * 10
    const passAlpha = ribbon.opacity * 0.09 / (pass + 1)

    ctx.beginPath()
    for (let i = 0; i < centerLine.length; i++) {
      const p = centerLine[i]
      const u = i / centerLine.length

      // How far from the focus points? Further = more blurred
      const d1 = 1 - Math.pow(Math.abs(u - focus1) * 2.5, 2)
      const d2 = 1 - Math.pow(Math.abs(u - focus2) * 2.5, 2)
      const blur = Math.max(0, Math.max(d1, d2))

      const y = p.y + p.w + spread * blur
      i === 0 ? ctx.moveTo(p.x, y) : ctx.lineTo(p.x, y)
    }
    // Return along the original edge
    for (let i = centerLine.length - 1; i >= 0; i--) {
      const p = centerLine[i]
      ctx.lineTo(p.x, p.y + p.w)
    }
    ctx.closePath()
    const col = cs[(pass + 1) % cs.length]
    ctx.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${passAlpha.toFixed(3)})`
    ctx.fill()
  }

  // Top edge blur — same idea, different phase
  const focus3 = (Math.sin(t * blurSpeed1 * 1.3 + ribbon.seed + 5) + 1) / 2

  for (let pass = 0; pass < 3; pass++) {
    const spread = (pass + 1) * 8
    const passAlpha = ribbon.opacity * 0.07 / (pass + 1)

    ctx.beginPath()
    for (let i = 0; i < centerLine.length; i++) {
      const p = centerLine[i]
      const u = i / centerLine.length
      const d = 1 - Math.pow(Math.abs(u - focus3) * 2.8, 2)
      const blur = Math.max(0, d)
      const y = p.y - p.w - spread * blur
      i === 0 ? ctx.moveTo(p.x, y) : ctx.lineTo(p.x, y)
    }
    for (let i = centerLine.length - 1; i >= 0; i--) {
      ctx.lineTo(centerLine[i].x, centerLine[i].y - centerLine[i].w)
    }
    ctx.closePath()
    const col = cs[(pass + 3) % cs.length]
    ctx.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${passAlpha.toFixed(3)})`
    ctx.fill()
  }
}

function drawSkyGlow() {
  // Soft radial glow behind the aurora — like light reflecting off atmosphere
  const cs = colorSets[0]
  const [c0, c1] = cs
  const pulse = 0.7 + 0.3 * Math.sin(t * 0.0003)

  // Main glow — centered where the ribbons are
  const gx = W * 0.55, gy = H * 0.18
  const gr = Math.max(W, H) * 0.5
  const glow = ctx.createRadialGradient(gx, gy, 0, gx, gy, gr)
  glow.addColorStop(0, `rgba(${c0[0]},${c0[1]},${c0[2]},${(0.06 * pulse).toFixed(3)})`)
  glow.addColorStop(0.3, `rgba(${c1[0]},${c1[1]},${c1[2]},${(0.03 * pulse).toFixed(3)})`)
  glow.addColorStop(0.6, `rgba(${c1[0]},${c1[1]},${c1[2]},${(0.01 * pulse).toFixed(3)})`)
  glow.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = glow
  ctx.fillRect(0, 0, W, H)

  // Top-to-bottom atmospheric gradient
  const atm = ctx.createLinearGradient(0, 0, 0, H * 0.5)
  atm.addColorStop(0, `rgba(${c1[0]},${c1[1]},${c1[2]},${(0.02 * pulse).toFixed(3)})`)
  atm.addColorStop(0.5, `rgba(${c0[0]},${c0[1]},${c0[2]},${(0.015 * pulse).toFixed(3)})`)
  atm.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = atm
  ctx.fillRect(0, 0, W, H * 0.5)
}

function drawFoggyRibbon(ribbon) {
  // Wider, more transparent version of the ribbon — creates foggy halo
  const cs = colorSets[ribbon.colSet % colorSets.length]
  const pts = 40 // lower res for fog
  const yCenter = ribbon.yBase * H

  const centerLine = []
  for (let i = 0; i <= pts; i++) {
    const u = i / pts
    const x = u * W * 1.2 - W * 0.1
    // Same flow but slightly offset in time — fog trails the sharp ribbon
    const flow1 = noise(u * 1.5 + ribbon.seed, t * 0.00007 * ribbon.speed, 0) * H * 0.15
    const flow2 = noise(u * 3.5 + ribbon.seed + 40, t * 0.00016 * ribbon.speed, 10) * H * 0.06
    const y = yCenter + flow1 + flow2
    // Fog is wider — 2.5x the ribbon width
    const widthMod = 0.4 + 0.6 * noise(u * 1.5 + ribbon.seed + 60, t * 0.0001 * ribbon.speed, 30)
    const w = ribbon.width * H * widthMod * 2.5
    centerLine.push({ x, y, w })
  }

  ctx.beginPath()
  ctx.moveTo(centerLine[0].x, centerLine[0].y - centerLine[0].w)
  for (let i = 1; i < centerLine.length; i++) {
    const prev = centerLine[i - 1], curr = centerLine[i]
    ctx.quadraticCurveTo(prev.x, prev.y - prev.w, (prev.x + curr.x) / 2, ((prev.y - prev.w) + (curr.y - curr.w)) / 2)
  }
  for (let i = centerLine.length - 1; i >= 0; i--) {
    const curr = centerLine[i], prev = i > 0 ? centerLine[i - 1] : centerLine[0]
    ctx.quadraticCurveTo(curr.x, curr.y + curr.w, (curr.x + prev.x) / 2, ((curr.y + curr.w) + (prev.y + prev.w)) / 2)
  }
  ctx.closePath()

  const a = ribbon.opacity * 0.25
  const grad = ctx.createLinearGradient(0, 0, W, 0)
  grad.addColorStop(0, `rgba(${cs[0][0]},${cs[0][1]},${cs[0][2]},0)`)
  grad.addColorStop(0.15, `rgba(${cs[1][0]},${cs[1][1]},${cs[1][2]},${(a * 0.3).toFixed(3)})`)
  grad.addColorStop(0.35, `rgba(${cs[2][0]},${cs[2][1]},${cs[2][2]},${(a * 0.8).toFixed(3)})`)
  grad.addColorStop(0.55, `rgba(${cs[3][0]},${cs[3][1]},${cs[3][2]},${a.toFixed(3)})`)
  grad.addColorStop(0.75, `rgba(${cs[4][0]},${cs[4][1]},${cs[4][2]},${(a * 0.5).toFixed(3)})`)
  grad.addColorStop(1, `rgba(${cs[5][0]},${cs[5][1]},${cs[5][2]},0)`)
  ctx.fillStyle = grad
  ctx.fill()
}

function draw() {
  if (!ctx) { rafId = requestAnimationFrame(draw); return }
  ctx.clearRect(0, 0, W, H)

  drawStars()

  // Sky glow — atmospheric background
  drawSkyGlow()

  ctx.globalCompositeOperation = 'screen'

  // Foggy halos first (behind)
  for (const ribbon of RIBBONS) {
    drawFoggyRibbon(ribbon)
  }

  // Sharp ribbons on top
  for (const ribbon of RIBBONS) {
    drawRibbon(ribbon)
  }

  ctx.globalCompositeOperation = 'source-over'

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
.aurora-wrap { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; }
.aurora-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
</style>
