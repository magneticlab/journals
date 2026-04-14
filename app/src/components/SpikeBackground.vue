<template>
  <canvas ref="canvasEl" class="spike-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({ palette: { type: String, default: 'midnight' } })
const canvasEl = ref(null)
let ctx, W = 0, H = 0, rafId = 0, t = 0, schemeT = 0

const SCHEME_SETS = {
  midnight: [[[110,160,255],[140,120,255],[255,100,130],[255,180,60],[80,220,140],[110,160,255]]],
  dawn: [[[230,140,60],[240,120,80],[220,180,70],[200,150,90],[240,160,50],[230,140,60]]],
  daylight: [[[90,150,255],[70,200,200],[120,190,130],[80,160,240],[110,140,255],[90,150,255]]],
  dusk: [[[140,80,200],[200,50,140],[180,100,120],[120,70,200],[170,50,170],[140,80,200]]],
  aurora: [[[40,120,200],[50,160,180],[40,200,160],[100,80,240],[40,170,200],[40,120,200]]],
}
const SCHEMES = SCHEME_SETS[props.palette] || SCHEME_SETS.midnight
const SCHEME_HOLD = 600, SCHEME_FADE = 600, SCHEME_CYCLE = SCHEME_HOLD + SCHEME_FADE

function lerpRGB(a, b, f) { return [Math.round(a[0]+(b[0]-a[0])*f), Math.round(a[1]+(b[1]-a[1])*f), Math.round(a[2]+(b[2]-a[2])*f)] }
function lerpInScheme(scheme, u) { const s = Math.max(0,Math.min(1,u)) * (scheme.length-1), lo = Math.floor(s); return lerpRGB(scheme[lo], scheme[Math.min(lo+1,scheme.length-1)], s-lo) }
function schemeColor(u) {
  const pos = schemeT % (SCHEME_CYCLE * SCHEMES.length), idx = Math.floor(pos / SCHEME_CYCLE) % SCHEMES.length, within = pos % SCHEME_CYCLE
  const a = lerpInScheme(SCHEMES[idx], u)
  if (within < SCHEME_HOLD) return a
  const f = ((within - SCHEME_HOLD) / SCHEME_FADE); return lerpRGB(a, lerpInScheme(SCHEMES[(idx+1)%SCHEMES.length], u), f < 0.5 ? 2*f*f : 1-Math.pow(-2*f+2,2)/2)
}

const SPIKE_COUNT = 500
let spikes = []

function buildSpikes() {
  spikes = []
  if (!W || !H) return
  const maxR = Math.min(W * 0.45, H * 0.6)
  for (let i = 0; i < SPIKE_COUNT; i++) {
    const angle = (Math.PI * 2 * i) / SPIKE_COUNT + (Math.random()-0.5) * (Math.PI*2/SPIKE_COUNT) * 0.5
    const r = Math.random()
    let restLen
    if (r < 0.15) restLen = maxR * (0.06 + Math.random()*0.2)
    else if (r < 0.25) restLen = maxR * (0.7 + Math.random()*0.3)
    else restLen = maxR * (0.3 + Math.random()*0.5)

    const rp = () => Math.random() * Math.PI * 2
    spikes.push({
      angle, restLen, len: restLen,
      p1: rp(), p2: rp(), p3: rp(),
      angFreq: 0.00018 + Math.random()*0.0004,
      lenFreq: 0.00012 + Math.random()*0.0003,
      angAmp: 0.02 + Math.random()*0.05,
      lenAmp: 0.04 + Math.random()*0.08,
      width: 0.3 + Math.random()*0.7,
      opacity: 0.08 + Math.random()*0.25,
      tipFreq: 0.0001 + Math.random()*0.0002,
      tipPhase: rp(),
    })
  }
}

function draw() {
  if (!ctx || !W) { rafId = requestAnimationFrame(draw); return }
  ctx.clearRect(0, 0, W, H)
  const cx = W * 0.5, cy = H * 0.15 // top center

  // Subtle glow
  const glowR = Math.min(W, H) * 0.8
  const [gr,gg,gb] = schemeColor(0.5)
  const glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, glowR)
  glow.addColorStop(0, `rgba(${gr},${gg},${gb},0.12)`)
  glow.addColorStop(0.4, `rgba(${gr},${gg},${gb},0.04)`)
  glow.addColorStop(1, `rgba(${gr},${gg},${gb},0)`)
  ctx.fillStyle = glow; ctx.fillRect(0, 0, W, H)

  const globalSway = Math.sin(t * 0.00005) * 0.01

  for (const s of spikes) {
    const ang = s.angle + globalSway + s.angAmp * Math.sin(t * s.angFreq + s.p1) + s.angAmp * 0.3 * Math.sin(t * s.angFreq * 1.7 + s.p2)
    const len = s.restLen + s.restLen * s.lenAmp * Math.sin(t * s.lenFreq + s.p3)
    if (len < 2) continue

    const tipX = cx + Math.sin(ang) * len
    const tipY = cy - Math.cos(ang) * len
    const tipFade = Math.max(0, Math.min(1, 0.5 + Math.sin(t * s.tipFreq + s.tipPhase) * 0.4))

    const u = ((ang % (Math.PI*2)) + Math.PI*2) % (Math.PI*2) / (Math.PI*2)
    const [rv,gv,bv] = schemeColor(u)
    const alpha = s.opacity * tipFade

    const grad = ctx.createLinearGradient(cx, cy, tipX, tipY)
    grad.addColorStop(0, `rgba(${rv},${gv},${bv},0)`)
    grad.addColorStop(0.3, `rgba(${rv},${gv},${bv},${alpha*0.05})`)
    grad.addColorStop(0.7, `rgba(${rv},${gv},${bv},${alpha*0.2})`)
    grad.addColorStop(1, `rgba(${rv},${gv},${bv},${alpha})`)

    ctx.beginPath(); ctx.moveTo(cx, cy)
    const mid = len * 0.45
    const perp = Math.sin(t * s.angFreq * 0.5 + s.p2) * 1.2
    ctx.quadraticCurveTo(cx + Math.sin(ang)*mid + Math.cos(ang)*perp, cy - Math.cos(ang)*mid - Math.sin(ang)*perp, tipX, tipY)
    ctx.strokeStyle = grad; ctx.lineWidth = s.width; ctx.stroke()

    if (alpha > 0.02) {
      ctx.beginPath(); ctx.arc(tipX, tipY, 1.5, 0, Math.PI*2)
      ctx.fillStyle = `rgba(${rv},${gv},${bv},${alpha*0.8})`; ctx.fill()
    }
  }
  schemeT++; t++; rafId = requestAnimationFrame(draw)
}

function resize() {
  if (!canvasEl.value) return
  const dpr = window.devicePixelRatio || 1
  W = canvasEl.value.offsetWidth; H = canvasEl.value.offsetHeight
  canvasEl.value.width = W * dpr; canvasEl.value.height = H * dpr
  ctx = canvasEl.value.getContext('2d'); ctx.scale(dpr, dpr); buildSpikes()
}

onMounted(() => { resize(); window.addEventListener('resize', resize); draw() })
onUnmounted(() => { window.removeEventListener('resize', resize); cancelAnimationFrame(rafId) })
</script>

<style scoped>
.spike-canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; }
</style>
