<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics: Object,
  brandColor: { type: String, default: '#6395ff' },
  size: { type: Number, default: 260 },
})

const keys = computed(() => Object.keys(props.metrics || {}))
const values = computed(() => keys.value.map(k => props.metrics[k].score))
const labels = computed(() => keys.value.map(k => {
  const l = props.metrics[k].label
  // Shorten for display
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
      </defs>

      <!-- Grid framework — visible -->
      <path v-for="ring in [0.25, 0.5, 0.75, 1.0]" :key="ring" :d="hexPath(ring)"
        fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.75" />

      <!-- Spokes -->
      <line v-for="i in n" :key="'s'+i"
        :x1="cx" :y1="cy" :x2="pt(i-1,1)[0]" :y2="pt(i-1,1)[1]"
        stroke="rgba(255,255,255,0.07)" stroke-width="0.75" />

      <!-- Data shape — glow -->
      <path :d="dataPath" :fill="brandColor + '18'"
        :stroke="brandColor" stroke-width="1.5" stroke-linejoin="round"
        :filter="`url(#${uid}-glow)`" opacity="0.4" />

      <!-- Data shape — crisp -->
      <path :d="dataPath" :fill="brandColor + '18'"
        :stroke="brandColor" stroke-width="1.5" stroke-linejoin="round"
        stroke-opacity="0.9" />

      <!-- Score values at each vertex -->
      <template v-for="(v, i) in values" :key="'v'+i">
        <text :x="scoreXY(i)[0]" :y="scoreXY(i)[1]"
          text-anchor="middle" dominant-baseline="middle"
          class="score-num" :fill="brandColor">{{ v }}</text>
      </template>

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
