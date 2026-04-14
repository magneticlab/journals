<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics: Object,
  brandColor: { type: String, default: '#6395ff' },
  size: { type: Number, default: 240 },
})

const keys = computed(() => Object.keys(props.metrics || {}))
const values = computed(() => keys.value.map(k => props.metrics[k].score))
const labels = computed(() => keys.value.map(k => props.metrics[k].label))
const n = computed(() => keys.value.length)
const cx = computed(() => props.size / 2)
const cy = computed(() => props.size / 2)
const radius = computed(() => props.size / 2 - 32)

function point(i, r) {
  const angle = (Math.PI * 2 * i) / n.value - Math.PI / 2
  return {
    x: cx.value + Math.cos(angle) * radius.value * r,
    y: cy.value + Math.sin(angle) * radius.value * r,
  }
}

const rings = [0.2, 0.4, 0.6, 0.8, 1.0]

function ringPath(r) {
  const pts = Array.from({ length: n.value }, (_, i) => point(i, r))
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + ' Z'
}

const dataPath = computed(() => {
  const pts = values.value.map((v, i) => point(i, v / 100))
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + ' Z'
})

function labelPos(i) {
  const angle = (Math.PI * 2 * i) / n.value - Math.PI / 2
  const lr = radius.value + 22
  return { x: cx.value + Math.cos(angle) * lr, y: cy.value + Math.sin(angle) * lr }
}

// Average score for stroke color
const avgScore = computed(() => {
  const sum = values.value.reduce((a, b) => a + b, 0)
  return sum / values.value.length
})

function scoreColor(s) {
  if (s >= 80) return '#34d399'
  if (s >= 60) return '#6395ff'
  if (s >= 40) return '#fbbf24'
  return '#f87171'
}

const strokeColor = computed(() => scoreColor(avgScore.value))

// Unique ID for gradient
const gradId = computed(() => 'radar-grad-' + Math.random().toString(36).slice(2, 8))
</script>

<template>
  <div class="radar-wrap">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <defs>
        <!-- Radial gradient: red center → amber → blue → green edge -->
        <radialGradient :id="gradId" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#f87171" stop-opacity="0.25" />
          <stop offset="30%" stop-color="#fbbf24" stop-opacity="0.18" />
          <stop offset="60%" stop-color="#6395ff" stop-opacity="0.14" />
          <stop offset="100%" stop-color="#34d399" stop-opacity="0.12" />
        </radialGradient>
      </defs>

      <!-- Zone rings with color tint -->
      <path :d="ringPath(0.4)" fill="rgba(248,113,113,0.04)" stroke="none" />
      <path :d="ringPath(0.6)" fill="rgba(251,191,36,0.03)" stroke="none" />
      <path :d="ringPath(0.8)" fill="rgba(99,149,255,0.02)" stroke="none" />
      <path :d="ringPath(1.0)" fill="rgba(52,211,153,0.02)" stroke="none" />

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

      <!-- Data fill — radial gradient from red center to green edge -->
      <path
        :d="dataPath"
        :fill="`url(#${gradId})`"
        :stroke="strokeColor"
        stroke-width="1.5"
        stroke-linejoin="round"
        stroke-opacity="0.7"
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
