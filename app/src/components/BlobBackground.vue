<template>
  <canvas ref="canvasEl" class="blob-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  palette: { type: String, default: 'dark' }
})

const canvasEl = ref(null)
let ctx, W = 0, H = 0, rafId = 0, t = 0, schemeT = 0

// Color schemes — adapted for dark theme (muted, deeper)
const SCHEMES_DARK = [
  [[95,40,250],[70,110,255],[40,175,255],[35,215,230],[65,225,215],[95,40,250]],
  [[30,190,245],[25,215,220],[40,225,185],[70,230,155],[50,200,230],[30,190,245]],
  [[220,210,50],[255,170,45],[255,120,75],[255,85,135],[240,145,55],[220,210,50]],
  [[255,90,150],[240,70,195],[205,55,230],[160,45,245],[225,65,210],[255,90,150]],
]

const SCHEMES_AURORA = [
  [[40,120,200],[60,80,220],[50,160,180],[40,200,160],[70,140,220],[40,120,200]],
  [[30,180,160],[50,200,140],[80,190,120],[40,170,180],[60,160,200],[30,180,160]],
  [[80,60,200],[100,40,240],[70,100,220],[90,80,190],[60,120,210],[80,60,200]],
  [[40,160,220],[30,200,180],[50,180,200],[70,140,240],[40,170,200],[40,160,220]],
]

const SCHEMES = props.palette === 'aurora' ? SCHEMES_AURORA : SCHEMES_DARK

const SCHEME_HOLD = 600
const SCHEME_FADE = 600
const SCHEME_CYCLE = SCHEME_HOLD + SCHEME_FADE

function easeInOut(x) { return x < 0.5 ? 2*x*x : 1 - Math.pow(-2*x+2, 2)/2 }
function lerpRGB(a, b, f) { return [Math.round(a[0]+(b[0]-a[0])*f), Math.round(a[1]+(b[1]-a[1])*f), Math.round(a[2]+(b[2]-a[2])*f)] }

function lerpInScheme(scheme, u) {
  const cycled = (u * 1.7) % 1
  const scaled = cycled * (scheme.length - 1)
  const lo = Math.floor(scaled)
  const hi = Math.min(lo + 1, scheme.length - 1)
  return lerpRGB(scheme[lo], scheme[hi], scaled - lo)
}

function layerColor(u, schemeOffset) {
  const pos = schemeT % (SCHEME_CYCLE * SCHEMES.length)
  const rawIdx = Math.floor(pos / SCHEME_CYCLE)
  const idx = (rawIdx + schemeOffset + SCHEMES.length) % SCHEMES.length
  const within = pos % SCHEME_CYCLE
  const colorA = lerpInScheme(SCHEMES[idx], u)
  if (within < SCHEME_HOLD) return colorA
  const f = easeInOut((within - SCHEME_HOLD) / SCHEME_FADE)
  const colorB = lerpInScheme(SCHEMES[(idx + 1) % SCHEMES.length], u)
  return lerpRGB(colorA, colorB, f)
}

const HARMONICS = [
  { h: 3, amp: 0.13, freq: 0.0022, phase: 0.0 },
  { h: 5, amp: 0.08, freq: 0.0035, phase: 1.9 },
  { h: 2, amp: 0.06, freq: 0.0018, phase: 3.3 },
  { h: 7, amp: 0.03, freq: 0.0058, phase: 0.7 },
]
const N_PTS = 12
let primaryMaxR = 0

function computeSizes() { primaryMaxR = Math.min(W, H) * 0.58 }

function drawBlobSet(ancX, ancY, mox, moy, maxR, nLayers, schemeOffset, opacityScale, xScale, yScale, tOffset, driftBasePhase) {
  const half = (nLayers - 1) / 2
  const tc = t + tOffset

  for (let i = 0; i < nLayers; i++) {
    const u = i / (nLayers - 1)
    const r = maxR * (1 - u * 0.78)
    if (r < 2) continue

    const distFromMid = Math.abs(i - half) / half
    const centerFactor = Math.pow(1 - distFromMid, 1.6)
    const opacity = (0.08 + centerFactor * 0.22) * opacityScale

    const [rv, gv, bv] = layerColor(u, schemeOffset)

    const driftAmp = 4 + (1 - u) * 22
    const driftFreq = 0.0025 + (i % 7) * 0.0003
    const driftPhase = (i / nLayers) * Math.PI * 7.1 + driftBasePhase
    const driftSign = i % 2 === 0 ? 1 : -1
    const shapeShift = (i / nLayers) * Math.PI * 2.5

    const ox = ancX + mox + driftAmp * Math.sin(tc * driftFreq + driftPhase) * driftSign
    const oy = ancY + moy + driftAmp * Math.cos(tc * driftFreq * 0.72 + driftPhase + 1.3) * driftSign

    const pts = []
    for (let p = 0; p < N_PTS; p++) {
      const base = (p / N_PTS) * Math.PI * 2
      let mult = 1
      for (const h of HARMONICS) mult += h.amp * Math.sin(h.freq * tc + h.phase + shapeShift + base * h.h)
      mult = Math.max(0.52, mult)
      pts.push([ox + r * xScale * mult * Math.cos(base), oy + r * yScale * mult * Math.sin(base)])
    }

    ctx.beginPath()
    const last = pts[N_PTS - 1]
    ctx.moveTo((last[0] + pts[0][0]) / 2, (last[1] + pts[0][1]) / 2)
    for (let p = 0; p < N_PTS; p++) {
      const cur = pts[p], next = pts[(p + 1) % N_PTS]
      ctx.quadraticCurveTo(cur[0], cur[1], (cur[0] + next[0]) / 2, (cur[1] + next[1]) / 2)
    }
    ctx.closePath()

    const grad = ctx.createRadialGradient(ox, oy, r * 0.20, ox, oy, r * 1.15)
    grad.addColorStop(0, `rgba(${rv},${gv},${bv},${opacity.toFixed(3)})`)
    grad.addColorStop(0.62, `rgba(${rv},${gv},${bv},${opacity.toFixed(3)})`)
    grad.addColorStop(1, `rgba(${rv},${gv},${bv},0)`)
    ctx.fillStyle = grad
    ctx.fill()
  }
}

function draw() {
  if (!ctx) return
  ctx.clearRect(0, 0, W, H)

  // Single large blob — top right, bleeding out
  drawBlobSet(
    W * 0.75, H * 0.15,
    20 * Math.sin(t * 0.00022),
    14 * Math.cos(t * 0.00017),
    primaryMaxR, 48, 0, 1.0, 1.15, 0.90, 0, 0
  )

  schemeT++
  t++
  rafId = requestAnimationFrame(draw)
}

function resize() {
  if (!canvasEl.value) return
  const dpr = window.devicePixelRatio || 1
  W = canvasEl.value.offsetWidth
  H = canvasEl.value.offsetHeight
  canvasEl.value.width = W * dpr
  canvasEl.value.height = H * dpr
  ctx = canvasEl.value.getContext('2d')
  ctx.scale(dpr, dpr)
  computeSizes()
}

onMounted(() => { resize(); window.addEventListener('resize', resize); draw() })
onUnmounted(() => { window.removeEventListener('resize', resize); cancelAnimationFrame(rafId) })
</script>

<style scoped>
.blob-canvas {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  pointer-events: none; z-index: 0;
}
</style>
