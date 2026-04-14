<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ journal: String })
const router = useRouter()
const manifest = ref({ work: [], daily: [] })
const search = ref('')

onMounted(async () => { manifest.value = await (await fetch('/manifest.json')).json() })

const entries = computed(() => manifest.value[props.journal] || [])
const filtered = computed(() => {
  if (!search.value) return entries.value
  const q = search.value.toLowerCase()
  return entries.value.filter(e => e.date.includes(q) || e.day.toLowerCase().includes(q) || e.summary.toLowerCase().includes(q))
})
const title = computed(() => props.journal === 'work' ? 'Work Journal' : 'Daily Journal')
const isWork = computed(() => props.journal === 'work')

// Latest entry
const latest = computed(() => entries.value[0] || null)

// 7-day sparkline data
const last7 = computed(() => {
  const slice = entries.value.slice(0, 7).reverse()
  return slice.map(e => ({
    date: e.date.slice(5), // MM-DD
    day: e.day?.slice(0, 1),
    value: isWork.value ? (e.stats?.commits || 0) : (e.stats?.commits || 0),
    sessions: e.stats?.sessions || 0,
    commands: e.stats?.commands || 0,
  }))
})
const sparkMax = computed(() => Math.max(...last7.value.map(d => d.value), 1))

// Group by month
const grouped = computed(() => {
  const groups = {}
  for (const e of filtered.value) {
    const month = e.date.slice(0, 7) // YYYY-MM
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
</script>

<template>
  <div class="page">
    <!-- Sub-header -->
    <div class="subheader">
      <div class="mx header-inner">
        <div class="header-left">
          <router-link to="/" class="back-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </router-link>
          <div>
            <p class="label">{{ title }}</p>
            <h1 class="htitle">{{ isWork ? 'Sessions & Commits' : 'Terminal & Files' }}</h1>
          </div>
        </div>
      </div>
    </div>

    <div class="mx body">

      <!-- Featured Latest Report -->
      <div v-if="latest" class="featured" @click="router.push(`/${journal}/${latest.date}`)">
        <div class="featured-left">
          <p class="featured-label">Latest Report</p>
          <h2 class="featured-date">{{ latest.day }}, {{ latest.display }}</h2>
          <p class="featured-summary">{{ latest.summary }}</p>
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
        <div class="featured-arrow">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
        </div>
      </div>

      <!-- 7-Day Sparkline -->
      <div v-if="last7.length" class="spark-card">
        <p class="section-label">Last 7 Days — Commits</p>
        <div class="spark-chart">
          <div v-for="d in last7" :key="d.date" class="spark-col">
            <div class="spark-bar-wrap">
              <div class="spark-bar" :style="{ height: (d.value / sparkMax * 100) + '%' }">
                <span class="spark-val" v-if="d.value">{{ d.value }}</span>
              </div>
            </div>
            <span class="spark-label">{{ d.date }}</span>
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
            <div class="month-dot"></div>
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
              <div class="entry-dot"></div>
              <div class="entry-content">
                <div class="entry-top">
                  <span class="entry-date">{{ e.date.slice(8) }}</span>
                  <span class="entry-day">{{ e.day?.slice(0, 3) }}</span>
                  <span class="entry-stats" v-if="isWork">{{ e.stats?.sessions || 0 }}s · {{ e.stats?.commits || 0 }}c</span>
                  <span class="entry-stats" v-else>{{ e.stats?.commands || 0 }} cmd · {{ e.stats?.commits || 0 }}c</span>
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
.subheader { border-bottom: 1px solid var(--border); background: var(--bg-card); padding: 20px 0; }
.mx { max-width: 880px; margin: 0 auto; padding-left: 24px; padding-right: 24px; }
.header-inner { display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 12px; }
.back-btn { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--border); color: var(--text-muted); transition: all 0.15s; flex-shrink: 0; }
.back-btn:hover { border-color: var(--border-hover); color: var(--text-strong); }
.label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em; color: var(--text-muted); }
.htitle { margin-top: 2px; font-family: var(--serif); font-size: 22px; font-weight: 400; color: var(--text-heading); }

.body { padding: 24px 0 64px; }

/* Featured card */
.featured {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
  padding: 24px; margin-bottom: 16px; cursor: pointer; transition: border-color 0.2s;
  display: flex; align-items: center; justify-content: space-between;
}
.featured:hover { border-color: var(--border-hover); }
.featured-left { flex: 1; }
.featured-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.15em; color: var(--blue); margin-bottom: 6px; }
.featured-date { font-family: var(--serif); font-size: 20px; font-weight: 400; color: var(--text-heading); margin-bottom: 4px; }
.featured-summary { font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }
.featured-stats { display: flex; gap: 24px; padding-top: 14px; border-top: 1px solid var(--border); }
.fstat { display: flex; flex-direction: column; gap: 2px; }
.fstat-val { font-size: 18px; font-weight: 700; color: var(--text-heading); font-variant-numeric: tabular-nums; }
.fstat-label { font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); }
.featured-arrow { color: var(--text-muted); flex-shrink: 0; margin-left: 16px; }

/* Sparkline */
.spark-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
  padding: 20px 24px; margin-bottom: 24px;
}
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 16px; }
.spark-chart { display: flex; gap: 6px; align-items: flex-end; height: 100px; }
.spark-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.spark-bar-wrap { width: 100%; height: 80px; display: flex; align-items: flex-end; justify-content: center; }
.spark-bar { width: 100%; min-height: 3px; background: var(--blue); border-radius: 4px 4px 2px 2px; position: relative; transition: height 0.3s; }
.spark-val { position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: 10px; font-weight: 600; color: var(--text-strong); font-variant-numeric: tabular-nums; }
.spark-label { font-size: 10px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

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
.month-dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--border-hover); background: var(--bg); flex-shrink: 0; }
.month-label { font-family: var(--serif); font-size: 15px; color: var(--text-heading); }
.month-count { font-size: 11px; color: var(--text-muted); }

.month-entries { padding-left: 4px; }
.entry-row {
  display: flex; align-items: stretch; cursor: pointer; position: relative;
  transition: background 0.1s; border-radius: 8px;
  margin-left: 1px;
}
.entry-row:hover { background: var(--bg-card); }
.entry-row:hover .entry-dot { background: var(--blue); border-color: var(--blue); }

.entry-line {
  position: absolute; left: 4px; top: 0; bottom: 0; width: 1px;
  background: var(--border);
}
.entry-dot {
  width: 7px; height: 7px; border-radius: 50%; border: 1.5px solid var(--border-hover);
  background: var(--bg); flex-shrink: 0; margin-top: 14px; margin-right: 12px;
  position: relative; z-index: 1; transition: all 0.15s;
}
.entry-content { flex: 1; padding: 8px 12px 8px 0; }
.entry-top { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.entry-date { font-size: 14px; font-weight: 600; color: var(--text-strong); font-variant-numeric: tabular-nums; }
.entry-day { font-size: 12px; color: var(--text-muted); }
.entry-stats { font-size: 11px; color: var(--text-muted); margin-left: auto; font-variant-numeric: tabular-nums; }
.entry-summary { font-size: 12px; color: var(--text-muted); line-height: 1.5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 640px) {
  .header-inner { flex-direction: column; align-items: flex-start; gap: 12px; }
  .featured { flex-direction: column; }
  .featured-arrow { display: none; }
}
</style>
