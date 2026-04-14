<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics: Object,
  brandColor: { type: String, default: '#6395ff' },
  size: { type: Number, default: 280 },
})

const keys = computed(() => Object.keys(props.metrics || {}))
const values = computed(() => keys.value.map(k => props.metrics[k].score))
const labels = computed(() => keys.value.map(k => {
  const l = props.metrics[k].label
  if (l === 'Output Volume') return 'Output'
  return l
}))
const n = computed(() => keys.value.length)
const cx = computed(() => props.size / 2)
const cy = computed(() => props.size / 2)
const r = computed(() => props.size / 2 - 36)

function pt(i, ratio) {
  const a = (Math.PI * 2 * i) / n.value - Math.PI / 2
  return [cx.value + Math.cos(a) * r.value * ratio, cy.value + Math.sin(a) * r.value * ratio]
}

function hexPath(ratio) {
  return Array.from({ length: n.value }, (_, i) => {
    const [x, y] = pt(i, ratio)
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ') + ' Z'
}

const dataPath = computed(() => {
  return values.value.map((v, i) => {
    const [x, y] = pt(i, v / 100)
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ') + ' Z'
})

const edges = computed(() => {
  return values.value.map((v, i) => {
    const next = (i + 1) % n.value
    const [x1, y1] = pt(i, v / 100)
    const [x2, y2] = pt(next, values.value[next] / 100)
    return { x1, y1, x2, y2, c1: scoreColor(v), c2: scoreColor(values.value[next]) }
  })
})

function scoreColor(s) {
  if (s >= 80) return '#34d399'
  if (s >= 60) return '#6395ff'
  if (s >= 40) return '#fbbf24'
  return '#f87171'
}

function labelXY(i) {
  const a = (Math.PI * 2 * i) / n.value - Math.PI / 2
  const lr = r.value + 24
  return [cx.value + Math.cos(a) * lr, cy.value + Math.sin(a) * lr]
}

function scoreXY(i) {
  const v = values.value[i]
  const a = (Math.PI * 2 * i) / n.value - Math.PI / 2
  const sr = r.value * (v / 100) + 14
  return [cx.value + Math.cos(a) * sr, cy.value + Math.sin(a) * sr]
}

const uid = 'r' + Math.random().toString(36).slice(2, 6)
</script>

<template>
  <div class="radar">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <defs>
        <filter :id="uid + '-glow'">
          <feGaussianBlur stdDeviation="5" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>

        <!-- Radial gradient for the fill: red center → green edge -->
        <radialGradient :id="uid + '-fill'" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#f87171" stop-opacity="0.3" />
          <stop offset="35%" stop-color="#fbbf24" stop-opacity="0.2" />
          <stop offset="65%" stop-color="#6395ff" stop-opacity="0.15" />
          <stop offset="100%" stop-color="#34d399" stop-opacity="0.12" />
        </radialGradient>

        <!-- Per-edge gradients -->
        <linearGradient v-for="(e, i) in edges" :key="'g'+i" :id="uid + '-eg' + i"
          :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" gradientUnits="userSpaceOnUse">
          <stop offset="0%" :stop-color="e.c1" />
          <stop offset="100%" :stop-color="e.c2" />
        </linearGradient>
      </defs>

      <!-- Grid -->
      <path v-for="ring in [0.25, 0.5, 0.75, 1.0]" :key="ring" :d="hexPath(ring)"
        fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.75" />

      <!-- Spokes -->
      <line v-for="i in n" :key="'s'+i"
        :x1="cx" :y1="cy" :x2="pt(i-1,1)[0]" :y2="pt(i-1,1)[1]"
        stroke="rgba(255,255,255,0.07)" stroke-width="0.75" />

      <!-- Data fill — glow with radial gradient -->
      <path :d="dataPath" :fill="`url(#${uid}-fill)`"
        stroke="none"
        :filter="`url(#${uid}-glow)`" opacity="0.6" />

      <!-- Data fill — crisp with radial gradient -->
      <path :d="dataPath" :fill="`url(#${uid}-fill)`" stroke="none" />

      <!-- Per-edge gradient strokes -->
      <line v-for="(e, i) in edges" :key="'e'+i"
        :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
        :stroke="`url(#${uid}-eg${i})`" stroke-width="2"
        stroke-linecap="round" />

      <!-- Score values — colored by score -->
      <text v-for="(v, i) in values" :key="'v'+i"
        :x="scoreXY(i)[0]" :y="scoreXY(i)[1]"
        text-anchor="middle" dominant-baseline="middle"
        class="score-num" :fill="scoreColor(v)">{{ v }}</text>

      <!-- Axis labels -->
      <text v-for="(label, i) in labels" :key="'l'+i"
        :x="labelXY(i)[0]" :y="labelXY(i)[1]"
        text-anchor="middle" dominant-baseline="middle"
        class="axis-label">{{ label }}</text>
    </svg>
  </div>
</template>

<style scoped>
.radar { display: flex; align-items: center; justify-content: center; }
.axis-label { font-size: 8.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; fill: rgba(255,255,255,0.3); }
.score-num { font-size: 9px; font-weight: 700; font-variant-numeric: tabular-nums; }
</style>
