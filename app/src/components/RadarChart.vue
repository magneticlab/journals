<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics: Object, // { volume: { score, label }, complexity: { score, label }, ... }
  brandColor: { type: String, default: '#6395ff' },
  size: { type: Number, default: 220 },
})

const keys = computed(() => Object.keys(props.metrics || {}))
const values = computed(() => keys.value.map(k => props.metrics[k].score))
const labels = computed(() => keys.value.map(k => props.metrics[k].label))
const n = computed(() => keys.value.length)
const cx = computed(() => props.size / 2)
const cy = computed(() => props.size / 2)
const radius = computed(() => props.size / 2 - 32)

// Point on the hexagon at angle index i, at distance ratio r (0-1)
function point(i, r) {
  const angle = (Math.PI * 2 * i) / n.value - Math.PI / 2
  return {
    x: cx.value + Math.cos(angle) * radius.value * r,
    y: cy.value + Math.sin(angle) * radius.value * r,
  }
}

// Grid rings (20%, 40%, 60%, 80%, 100%)
const rings = [0.2, 0.4, 0.6, 0.8, 1.0]

function ringPath(r) {
  const pts = Array.from({ length: n.value }, (_, i) => point(i, r))
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + ' Z'
}

// Data polygon
const dataPath = computed(() => {
  const pts = values.value.map((v, i) => point(i, v / 100))
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + ' Z'
})

// Label positions — pushed slightly beyond the outer ring
function labelPos(i) {
  const angle = (Math.PI * 2 * i) / n.value - Math.PI / 2
  const lr = radius.value + 22
  return {
    x: cx.value + Math.cos(angle) * lr,
    y: cy.value + Math.sin(angle) * lr,
  }
}

// Score color
function scoreColor(s) {
  if (s >= 80) return '#34d399'
  if (s >= 60) return '#6395ff'
  if (s >= 40) return '#fbbf24'
  return '#f87171'
}

// Data point positions
const dataPoints = computed(() =>
  values.value.map((v, i) => ({ ...point(i, v / 100), score: v, color: scoreColor(v) }))
)
</script>

<template>
  <div class="radar-wrap">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <!-- Grid rings -->
      <path
        v-for="r in rings" :key="r"
        :d="ringPath(r)"
        fill="none"
        :stroke="r === 1 ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.04)'"
        stroke-width="1"
      />

      <!-- Axis lines -->
      <line
        v-for="i in n" :key="'axis-'+i"
        :x1="cx" :y1="cy"
        :x2="point(i - 1, 1).x" :y2="point(i - 1, 1).y"
        stroke="rgba(255,255,255,0.04)" stroke-width="1"
      />

      <!-- Data fill -->
      <path
        :d="dataPath"
        :fill="brandColor + '15'"
        :stroke="brandColor"
        stroke-width="2"
        stroke-linejoin="round"
      />

      <!-- Data points -->
      <circle
        v-for="(p, i) in dataPoints" :key="'pt-'+i"
        :cx="p.x" :cy="p.y" r="4"
        :fill="p.color"
        :stroke="p.color + '40'"
        stroke-width="3"
      />

      <!-- Labels -->
      <text
        v-for="(label, i) in labels" :key="'lbl-'+i"
        :x="labelPos(i).x" :y="labelPos(i).y"
        text-anchor="middle" dominant-baseline="middle"
        class="radar-label"
      >{{ label.split(' ')[0] }}</text>
    </svg>
  </div>
</template>

<style scoped>
.radar-wrap {
  display: flex; align-items: center; justify-content: center;
}
.radar-label {
  font-size: 9px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.06em; fill: var(--text-muted);
}
</style>
