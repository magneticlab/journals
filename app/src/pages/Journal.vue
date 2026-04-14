<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ journal: String })
const router = useRouter()
const manifest = ref({ work: [], daily: [] })
const search = ref('')
const sparkRange = ref(30)

onMounted(async () => { manifest.value = await (await fetch('/manifest.json')).json() })

const entries = computed(() => manifest.value[props.journal] || [])
const filtered = computed(() => {
  if (!search.value) return entries.value
  const q = search.value.toLowerCase()
  return entries.value.filter(e => e.date.includes(q) || e.day.toLowerCase().includes(q) || e.summary.toLowerCase().includes(q))
})
const isWork = computed(() => props.journal === 'work')
const title = computed(() => isWork.value ? 'Work Journal' : 'Daily Journal')
const latest = computed(() => entries.value[0] || null)
const latestData = ref(null)

// Load full latest entry for summary
import { watch } from 'vue'
watch(latest, async (l) => {
  if (!l) return
  try {
    const res = await fetch(`/entries/${props.journal}/${l.date}.json`)
    if (res.ok) latestData.value = await res.json()
  } catch {}
}, { immediate: true })

// Sparkline
const sparkData = computed(() => {
  const count = sparkRange.value === 0 ? entries.value.length : sparkRange.value
  const slice = entries.value.slice(0, count).reverse()
  return slice.map(e => ({
    date: e.date.slice(5),
    commits: e.stats?.commits || 0,
    sessions: e.stats?.sessions || 0,
    commands: e.stats?.commands || 0,
  }))
})
const sparkMax = computed(() => Math.max(...sparkData.value.map(d => d.commits), 1))

// Group by month
const grouped = computed(() => {
  const groups = {}
  for (const e of filtered.value) {
    const month = e.date.slice(0, 7)
    if (!groups[month]) groups[month] = []
    groups[month].push(e)
  }
  return groups
})

function monthLabel(ym) {
  const [y, m] = ym.split('-')
  const months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  return `${months[parseInt(m)]} ${y}`
}

// Featured card summary
const featuredSummary = computed(() => {
  if (!latestData.value) return ''
  const d = latestData.value
  if (d.wentRight) return d.wentRight
  return d.summary || ''
})

const featuredThemes = computed(() => {
  if (!latestData.value?.themes) return []
  return Object.keys(latestData.value.themes).filter(t => t !== 'General Development').slice(0, 4)
})
</script>

<template>
  <div class="page">
    <!-- Sub-header with branded icon -->
    <div class="subheader" @click="router.push('/')">
      <div class="mx header-inner">
        <div class="header-left">
          <div :class="['header-icon', isWork ? 'hicon-work' : 'hicon-daily']">
            <!-- Brand icon (default) -->
            <svg v-if="isWork" class="brand-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
            <svg v-else class="brand-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <!-- Back arrow (on hover) -->
            <svg class="back-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </div>
          <div>
            <p class="label">{{ title }}</p>
            <h1 class="htitle">{{ isWork ? 'Sessions & Commits' : 'Terminal & Files' }}</h1>
          </div>
        </div>
      </div>
    </div>

    <div class="mx body">

      <!-- Featured Latest Report -->
      <div v-if="latest" class="featured" :class="isWork ? 'featured-work' : 'featured-daily'" @click="router.push(`/${journal}/${latest.date}`)">
        <div class="featured-main">
          <p class="featured-label">Latest Report</p>
          <h2 class="featured-date">{{ latest.day }}, {{ latest.display }}</h2>
          <div class="featured-stats">
            <div class="fstat" v-if="isWork">
              <span class="fstat-val">{{ latest.stats?.sessions || 0 }}</span>
              <span class="fstat-label">Sessions</span>
            </div>
            <div class="fstat" v-if="isWork">
              <span class="fstat-val">{{ latest.stats?.commits || 0 }}</span>
              <span class="fstat-label">Commits</span>
            </div>
            <div class="fstat" v-if="!isWork">
              <span class="fstat-val">{{ latest.stats?.commands || 0 }}</span>
              <span class="fstat-label">Commands</span>
            </div>
            <div class="fstat" v-if="!isWork">
              <span class="fstat-val">{{ latest.stats?.commits || 0 }}</span>
              <span class="fstat-label">Commits</span>
            </div>
            <div class="fstat">
              <span class="fstat-val">{{ latest.stats?.repos || 0 }}</span>
              <span class="fstat-label">Repos</span>
            </div>
          </div>
        </div>
        <div class="featured-side">
          <p v-if="featuredSummary" class="featured-summary">{{ featuredSummary }}</p>
          <div v-if="featuredThemes.length" class="featured-themes">
            <span v-for="t in featuredThemes" :key="t" class="ftag">{{ t }}</span>
          </div>
          <div class="featured-arrow">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </div>
        </div>
      </div>

      <!-- Sparkline with range toggle -->
      <div class="spark-card">
        <div class="spark-header">
          <p class="section-label">Commits</p>
          <div class="range-toggle">
            <button :class="{ active: sparkRange === 30 }" @click="sparkRange = 30">30d</button>
            <button :class="{ active: sparkRange === 90 }" @click="sparkRange = 90">90d</button>
            <button :class="{ active: sparkRange === 0 }" @click="sparkRange = 0">All</button>
          </div>
        </div>
        <div class="spark-chart" v-if="sparkData.length">
          <div v-for="(d, i) in sparkData" :key="i" class="spark-col">
            <div class="spark-bar-wrap">
              <div :class="['spark-bar', isWork ? 'sbar-work' : 'sbar-daily']" :style="{ height: (d.commits / sparkMax * 100) + '%' }">
                <span class="spark-val" v-if="d.commits && sparkData.length <= 30">{{ d.commits }}</span>
              </div>
            </div>
            <span v-if="sparkData.length <= 30" class="spark-date">{{ d.date.slice(3) }}</span>
          </div>
        </div>
      </div>

      <!-- Search -->
      <div class="search-wrap">
        <input v-model="search" type="text" placeholder="Filter by date, day, or keyword..." class="search" />
        <span class="count">{{ filtered.length }} entries</span>
      </div>

      <!-- Timeline grouped by month -->
      <div class="timeline">
        <div v-for="(items, month) in grouped" :key="month" class="month-group">
          <div class="month-header">
            <div :class="['month-dot', isWork ? 'mdot-work' : 'mdot-daily']"></div>
            <span class="month-label">{{ monthLabel(month) }}</span>
            <span class="month-count">{{ items.length }} entries</span>
          </div>
          <div class="month-entries">
            <div
              v-for="e in items" :key="e.date"
              class="entry-row"
              @click="router.push(`/${journal}/${e.date}`)"
            >
              <div class="entry-line"></div>
              <div :class="['entry-dot', isWork ? 'edot-work' : 'edot-daily']"></div>
              <div class="entry-content">
                <div class="entry-top">
                  <span class="entry-date">{{ e.date.slice(8) }}</span>
                  <span class="entry-day">{{ e.day?.slice(0, 3) }}</span>
                  <div class="entry-meta" v-if="isWork">
                    <span class="meta-item"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg> {{ e.stats?.sessions || 0 }}</span>
                    <span class="meta-item"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg> {{ e.stats?.commits || 0 }}</span>
                  </div>
                  <div class="entry-meta" v-else>
                    <span class="meta-item"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 17l6-6-6-6"/><line x1="12" y1="19" x2="20" y2="19"/></svg> {{ e.stats?.commands || 0 }}</span>
                    <span class="meta-item"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg> {{ e.stats?.commits || 0 }}</span>
                  </div>
                </div>
                <p class="entry-summary">{{ e.summary }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.page { min-height: calc(100vh - 52px); }

/* Header */
.subheader { border-bottom: 1px solid var(--border); background: var(--bg-card); padding: 20px 0; cursor: pointer; transition: background 0.15s; }
.subheader:hover { background: var(--bg-elevated); }
.mx { max-width: 880px; margin: 0 auto; padding-left: 24px; padding-right: 24px; }
.header-inner { display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon {
  display: flex; align-items: center; justify-content: center;
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0; position: relative;
}
.hicon-work { background: rgba(59,130,246,0.1); color: var(--blue); }
.hicon-daily { background: rgba(34,197,94,0.1); color: var(--green); }
.brand-icon { transition: opacity 0.15s; }
.back-icon { position: absolute; opacity: 0; transition: opacity 0.15s; color: var(--text-strong); }
.subheader:hover .brand-icon { opacity: 0; }
.subheader:hover .back-icon { opacity: 1; }
.label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em; color: var(--text-muted); }
.htitle { margin-top: 2px; font-family: var(--serif); font-size: 24px; font-weight: 400; color: var(--text-heading); }

.body { padding: 24px 0 64px; }

/* Featured */
.featured {
  border-radius: 14px; padding: 24px; margin-bottom: 16px;
  cursor: pointer; transition: border-color 0.2s;
  display: flex; gap: 24px;
}
.featured-work { background: rgba(59,130,246,0.04); border: 1px solid rgba(59,130,246,0.15); }
.featured-work:hover { border-color: rgba(59,130,246,0.3); }
.featured-daily { background: rgba(34,197,94,0.04); border: 1px solid rgba(34,197,94,0.15); }
.featured-daily:hover { border-color: rgba(34,197,94,0.3); }

.featured-main { flex: 1; }
.featured-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 6px; }
.featured-date { font-family: var(--serif); font-size: 24px; font-weight: 400; color: var(--text-heading); margin-bottom: 16px; }
.featured-stats { display: flex; gap: 24px; }
.fstat { display: flex; flex-direction: column; gap: 2px; }
.fstat-val { font-size: 20px; font-weight: 700; color: var(--text-heading); font-variant-numeric: tabular-nums; }
.fstat-label { font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); }

.featured-side { display: flex; flex-direction: column; justify-content: space-between; max-width: 280px; }
.featured-summary { font-size: 12px; color: var(--text-muted); line-height: 1.6; margin-bottom: 10px; }
.featured-themes { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px; }
.ftag { font-size: 10px; color: var(--text-muted); padding: 2px 8px; border-radius: 4px; border: 1px solid var(--border); }
.featured-arrow { color: var(--text-muted); align-self: flex-end; }

/* Sparkline */
.spark-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 20px 24px; margin-bottom: 24px; }
.spark-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); }
.range-toggle { display: flex; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
.range-toggle button {
  font-size: 11px; font-weight: 500; font-family: inherit;
  padding: 4px 12px; border: none; cursor: pointer;
  background: transparent; color: var(--text-muted); transition: all 0.15s;
}
.range-toggle button:not(:last-child) { border-right: 1px solid var(--border); }
.range-toggle button.active { background: var(--bg-elevated); color: var(--text-heading); }
.range-toggle button:hover:not(.active) { color: var(--text-strong); }

.spark-chart { display: flex; gap: 2px; align-items: flex-end; height: 80px; }
.spark-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 0; }
.spark-bar-wrap { width: 100%; height: 64px; display: flex; align-items: flex-end; justify-content: center; }
.spark-bar { width: 100%; min-height: 2px; border-radius: 2px 2px 1px 1px; position: relative; transition: height 0.3s; }
.sbar-work { background: rgba(59,130,246,0.5); }
.sbar-daily { background: rgba(34,197,94,0.5); }
.spark-val { position: absolute; top: -16px; left: 50%; transform: translateX(-50%); font-size: 9px; font-weight: 600; color: var(--text-strong); font-variant-numeric: tabular-nums; white-space: nowrap; }
.spark-date { font-size: 9px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

/* Search */
.search-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.search { flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; font-size: 13px; color: var(--text-strong); outline: none; font-family: inherit; }
.search::placeholder { color: var(--text-muted); }
.search:focus { border-color: var(--border-hover); }
.count { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }

/* Timeline */
.timeline { position: relative; }
.month-group { margin-bottom: 8px; }
.month-header {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 0; position: sticky; top: 52px;
  background: var(--bg); z-index: 10;
}
.month-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.mdot-work { background: var(--blue); border: 2px solid rgba(59,130,246,0.3); }
.mdot-daily { background: var(--green); border: 2px solid rgba(34,197,94,0.3); }
.month-label { font-family: var(--serif); font-size: 15px; color: var(--text-heading); }
.month-count { font-size: 11px; color: var(--text-muted); }

.month-entries { padding-left: 4px; }
.entry-row { display: flex; align-items: stretch; cursor: pointer; position: relative; transition: background 0.1s; border-radius: 8px; margin-left: 1px; }
.entry-row:hover { background: var(--bg-card); }
.entry-row:hover .entry-dot { transform: scale(1.4); }
.entry-line { position: absolute; left: 4px; top: 0; bottom: 0; width: 1px; background: var(--border); }
.entry-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; margin-top: 14px; margin-right: 12px; position: relative; z-index: 1; transition: all 0.15s; }
.edot-work { background: rgba(59,130,246,0.5); border: 1.5px solid rgba(59,130,246,0.3); }
.edot-daily { background: rgba(34,197,94,0.5); border: 1.5px solid rgba(34,197,94,0.3); }
.entry-content { flex: 1; padding: 8px 12px 8px 0; }
.entry-top { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.entry-date { font-size: 14px; font-weight: 600; color: var(--text-strong); font-variant-numeric: tabular-nums; }
.entry-day { font-size: 12px; color: var(--text-muted); }
.entry-meta { display: flex; align-items: center; gap: 10px; margin-left: auto; }
.meta-item { display: flex; align-items: center; gap: 3px; font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
.meta-item svg { color: var(--text-muted); opacity: 0.6; }
.entry-summary { font-size: 12px; color: var(--text-muted); line-height: 1.5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 640px) {
  .featured { flex-direction: column; }
  .featured-side { max-width: 100%; }
  .entry-meta { display: none; }
}
</style>
