<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ journal: String })
const router = useRouter()
const manifest = ref({ work: [], daily: [] })
const search = ref('')
const sparkRange = ref(30)
const weather = ref(null)
const scrollY = ref(0)
function onScroll() { scrollY.value = window.scrollY }

const heroStyle = computed(() => ({
  transform: `translateY(${scrollY.value * 0.15}px)`,
  opacity: Math.max(1 - scrollY.value / 400, 0),
}))

onMounted(async () => {
  window.addEventListener('scroll', onScroll, { passive: true })
  manifest.value = await (await fetch('/manifest.json')).json()
  try {
    const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=37.98&longitude=23.73&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m&timezone=auto')
    if (res.ok) weather.value = await res.json()
  } catch {}
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const entries = computed(() => manifest.value[props.journal] || [])
const filtered = computed(() => {
  if (!search.value) return entries.value
  const q = search.value.toLowerCase()
  return entries.value.filter(e => e.date.includes(q) || e.day.toLowerCase().includes(q) || e.summary.toLowerCase().includes(q))
})
const isWork = computed(() => props.journal === 'work')
const title = computed(() => isWork.value ? 'Work Journal' : 'Daily Journal')
const subtitle = computed(() => isWork.value ? 'Claude Code sessions, git commits, project work.' : 'Terminal activity, file changes, development.')
const latest = computed(() => entries.value[0] || null)
const latestData = ref(null)

watch(latest, async (l) => {
  if (!l) return
  try {
    const res = await fetch(`/entries/${props.journal}/${l.date}.json`)
    if (res.ok) latestData.value = await res.json()
  } catch {}
}, { immediate: true })

const sparkData = computed(() => {
  const count = sparkRange.value === 0 ? entries.value.length : sparkRange.value
  return entries.value.slice(0, count).reverse().map(e => ({ date: e.date.slice(5), commits: e.stats?.commits || 0 }))
})
const sparkMax = computed(() => Math.max(...sparkData.value.map(d => d.commits), 1))

const grouped = computed(() => {
  const groups = {}
  for (const e of filtered.value) { const m = e.date.slice(0, 7); if (!groups[m]) groups[m] = []; groups[m].push(e) }
  return groups
})
function monthLabel(ym) {
  const months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  return `${months[parseInt(ym.slice(5))]} ${ym.slice(0, 4)}`
}

const themeIcons = { 'Design System': '⬡', 'Design & Layout': '◫', 'Page Building': '▦', 'Animation & Effects': '✦', 'Bug Fixes': '⚠', 'Git & Deployment': '⎇', 'Version Iteration': '↻', 'Refactoring': '⟲', 'Content & Copy': '¶', 'Planning & Strategy': '◈', 'General Development': '⌘' }
const featuredThemes = computed(() => {
  const src = isWork.value ? latestData.value?.themes : latestData.value?.categories
  if (!src) return []
  return Object.entries(src).filter(([t]) => t !== 'General Development' && t !== 'Other').slice(0, 5).map(([name, count]) => ({ name, count, icon: themeIcons[name] || '◆' }))
})
const featuredSummary = computed(() => latestData.value?.wentRight || latestData.value?.summary || latest.value?.summary || '')
const linesAdded = computed(() => latestData.value?.stats?.linesAdded || 0)
const linesRemoved = computed(() => latestData.value?.stats?.linesRemoved || 0)
const filesChanged = computed(() => latestData.value?.stats?.filesChanged || 0)
const brandColor = computed(() => isWork.value ? '#6395ff' : '#34d399')

const wxCodes = { 0: { l: 'Clear', i: '☀' }, 1: { l: 'Mostly clear', i: '🌤' }, 2: { l: 'Partly cloudy', i: '⛅' }, 3: { l: 'Overcast', i: '☁' }, 45: { l: 'Foggy', i: '🌫' }, 51: { l: 'Drizzle', i: '🌦' }, 61: { l: 'Rain', i: '🌧' }, 63: { l: 'Rain', i: '🌧' }, 80: { l: 'Showers', i: '🌦' }, 95: { l: 'Storm', i: '⛈' } }
const wx = computed(() => { if (!weather.value?.current) return null; const c = weather.value.current; const w = wxCodes[c.weather_code] || { l: '—', i: '🌡' }; return { ...w, temp: c.temperature_2m, hum: c.relative_humidity_2m, wind: c.wind_speed_10m } })
</script>

<template>
  <div class="page">
    <!-- Top zone — transparent -->
    <div class="top-zone">
      <div class="mx">
        <!-- Nav: logo + weather -->
        <div class="nav-row">
          <router-link to="/" class="hero-logo">Journals</router-link>
          <div v-if="wx" class="weather">
            <span class="wx-i">{{ wx.i }}</span>
            <span class="wx-t">{{ wx.temp }}°</span>
            <span class="wx-l">{{ wx.l }}</span>
          </div>
        </div>

        <!-- Hero — parallax + fade -->
        <div class="hero" :style="heroStyle">
          <div class="hero-title-row">
            <div :class="['hero-icon', isWork ? 'hicon-work' : 'hicon-daily']">
              <svg v-if="isWork" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
              <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <h1 class="hero-h1">{{ title }}</h1>
          </div>
          <p class="hero-sub">{{ subtitle }}</p>
        </div>
      </div>
    </div>

    <!-- Body zone — gradient fade -->
    <div class="body-zone">
      <div class="mx body">
        <!-- Featured -->
        <div v-if="latest" class="featured" @click="router.push(`/${journal}/${latest.date}`)">
          <div class="feat-row-top">
            <p class="feat-label" :style="{ color: brandColor }">Latest Report</p>
            <div class="feat-stats">
              <div class="fstat" v-if="isWork"><span class="fstat-val">{{ latest.stats?.sessions || 0 }}</span><span class="fstat-lbl">sessions</span></div>
              <div class="fstat"><span class="fstat-val">{{ latest.stats?.commits || 0 }}</span><span class="fstat-lbl">commits</span></div>
              <div class="fstat" v-if="!isWork"><span class="fstat-val">{{ latest.stats?.commands || 0 }}</span><span class="fstat-lbl">commands</span></div>
              <div class="fstat"><span class="fstat-val">{{ latest.stats?.repos || 0 }}</span><span class="fstat-lbl">repos</span></div>
            </div>
          </div>
          <h2 class="feat-date">{{ latest.day }}, {{ latest.display }}</h2>
          <p v-if="featuredSummary" class="feat-summary">{{ featuredSummary }}</p>
          <div class="feat-bottom">
            <div v-if="featuredThemes.length" class="feat-themes">
              <div v-for="t in featuredThemes" :key="t.name" class="theme-card"><span class="theme-icon">{{ t.icon }}</span><span class="theme-name">{{ t.name }}</span><span class="theme-count">{{ t.count }}</span></div>
            </div>
            <div class="feat-volume" v-if="linesAdded || latest.stats?.filesModified">
              <span v-if="linesAdded" class="vol-add">+{{ linesAdded.toLocaleString() }}</span>
              <span v-if="linesRemoved" class="vol-del">-{{ linesRemoved.toLocaleString() }}</span>
              <span class="vol-files">{{ filesChanged || latest.stats?.filesModified || 0 }} files</span>
            </div>
          </div>
        </div>

        <!-- Sparkline -->
        <div class="spark-card">
          <div class="spark-header"><p class="section-label">Commits</p>
            <div class="range-toggle"><button :class="{ active: sparkRange === 30 }" @click="sparkRange = 30">30d</button><button :class="{ active: sparkRange === 90 }" @click="sparkRange = 90">90d</button><button :class="{ active: sparkRange === 0 }" @click="sparkRange = 0">All</button></div>
          </div>
          <div class="spark-chart" v-if="sparkData.length">
            <div v-for="(d, i) in sparkData" :key="i" class="spark-col"><div class="spark-bar-wrap"><div class="spark-bar" :style="{ height: (d.commits / sparkMax * 100) + '%', background: brandColor + '70' }"><span class="spark-val" v-if="d.commits && sparkData.length <= 30">{{ d.commits }}</span></div></div><span v-if="sparkData.length <= 30" class="spark-date">{{ d.date.slice(3) }}</span></div>
          </div>
        </div>

        <!-- Search -->
        <div class="search-wrap"><input v-model="search" type="text" placeholder="Filter..." class="search" /><span class="count">{{ filtered.length }}</span></div>

        <!-- Timeline -->
        <div class="timeline">
          <div v-for="(items, month) in grouped" :key="month" class="month-group">
            <div class="month-header"><div class="month-dot" :style="{ background: brandColor, borderColor: brandColor + '40' }"></div><span class="month-label">{{ monthLabel(month) }}</span><span class="month-count">{{ items.length }}</span></div>
            <div class="month-entries">
              <div v-for="e in items" :key="e.date" class="entry-row" @click="router.push(`/${journal}/${e.date}`)">
                <div class="entry-line"></div><div class="entry-dot" :style="{ background: brandColor + '60', borderColor: brandColor + '30' }"></div>
                <div class="entry-content">
                  <div class="entry-top"><span class="entry-date">{{ e.date.slice(8) }}</span><span class="entry-day">{{ e.day?.slice(0, 3) }}</span>
                    <div class="entry-meta"><span v-if="isWork && e.stats?.sessions" class="meta-item">{{ e.stats.sessions }}s</span><span v-if="e.stats?.commits" class="meta-item">{{ e.stats.commits }}c</span><span v-if="isWork && e.stats?.linesAdded" class="meta-item meta-add">+{{ e.stats.linesAdded.toLocaleString() }}</span><span v-if="!isWork && e.stats?.commands" class="meta-item">{{ e.stats.commands }} cmd</span></div>
                  </div>
                  <p class="entry-summary">{{ e.summary }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; position: relative; z-index: 1; }
.mx { max-width: 880px; margin: 0 auto; padding-left: 24px; padding-right: 24px; }

/* Top zone */
.top-zone { padding: 48px 0 0; }
.nav-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px; }
.hero-logo { font-family: var(--serif); font-size: 20px; color: var(--text-heading); }
.hero-logo:hover { color: var(--text-muted); }
.weather { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); background: rgba(20,20,22,0.5); backdrop-filter: blur(12px); border: 1px solid var(--border); border-radius: 10px; padding: 6px 14px; }
.wx-i { font-size: 16px; } .wx-t { font-weight: 600; color: var(--text-strong); font-size: 14px; } .wx-l { color: var(--text); }

.hero { padding-bottom: 100px; will-change: transform, opacity; }
.hero-title-row { display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }
.hero-icon { display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 14px; flex-shrink: 0; }
.hicon-work { background: rgba(99,149,255,0.12); color: #6395ff; }
.hicon-daily { background: rgba(52,211,153,0.12); color: #34d399; }
.hero-h1 { font-family: var(--serif); font-size: 36px; font-weight: 400; color: var(--text-heading); }
.hero-sub { font-size: 14px; color: var(--text-muted); margin-left: 62px; }

/* Body zone */
.body-zone { position: relative; background: linear-gradient(to bottom, transparent 0%, #0c0c0e 150px); margin-top: -60px; padding-top: 60px; }
.body { padding-bottom: 64px; }

/* Featured */
.featured { border-radius: 16px; padding: 28px; margin-bottom: 16px; cursor: pointer; transition: all 0.2s; background: rgba(12,12,14,0.75); border: 1px solid var(--border); backdrop-filter: blur(16px); box-shadow: 0 4px 24px rgba(0,0,0,0.25); }
.featured:hover { border-color: var(--border-hover); box-shadow: 0 8px 32px rgba(0,0,0,0.35); transform: translateY(-1px); }
.feat-row-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.feat-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; }
.feat-stats { display: flex; gap: 16px; }
.fstat { display: flex; align-items: baseline; gap: 4px; }
.fstat-val { font-size: 18px; font-weight: 700; color: var(--text-heading); font-variant-numeric: tabular-nums; }
.fstat-lbl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.feat-date { font-family: var(--serif); font-size: 28px; font-weight: 400; color: var(--text-heading); margin-bottom: 10px; }
.feat-summary { font-size: 13px; color: var(--text); line-height: 1.65; margin-bottom: 18px; }
.feat-bottom { display: flex; align-items: center; justify-content: space-between; padding-top: 14px; border-top: 1px solid var(--border); }
.feat-themes { display: flex; gap: 6px; flex-wrap: wrap; }
.theme-card { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; background: var(--bg-elevated); border: 1px solid var(--border); }
.theme-icon { font-size: 12px; opacity: 0.5; } .theme-name { font-size: 12px; color: var(--text-strong); font-weight: 500; } .theme-count { font-size: 11px; color: var(--text-muted); }
.feat-volume { display: flex; gap: 10px; }
.vol-add { font-size: 12px; font-weight: 600; color: #34d399; } .vol-del { font-size: 12px; font-weight: 600; color: #f87171; } .vol-files { font-size: 12px; color: var(--text-muted); }

/* Sparkline */
.spark-card { background: rgba(12,12,14,0.6); border: 1px solid var(--border); border-radius: 14px; padding: 20px 24px; margin-bottom: 24px; backdrop-filter: blur(12px); }
.spark-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); }
.range-toggle { display: flex; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
.range-toggle button { font-size: 11px; font-weight: 500; font-family: inherit; padding: 4px 12px; border: none; cursor: pointer; background: transparent; color: var(--text-muted); transition: all 0.15s; }
.range-toggle button:not(:last-child) { border-right: 1px solid var(--border); }
.range-toggle button.active { background: var(--bg-elevated); color: var(--text-heading); }
.spark-chart { display: flex; gap: 2px; align-items: flex-end; height: 80px; }
.spark-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 0; }
.spark-bar-wrap { width: 100%; height: 64px; display: flex; align-items: flex-end; justify-content: center; }
.spark-bar { width: 100%; min-height: 2px; border-radius: 2px 2px 1px 1px; position: relative; transition: height 0.3s; }
.spark-val { position: absolute; top: -16px; left: 50%; transform: translateX(-50%); font-size: 9px; font-weight: 600; color: var(--text-strong); font-variant-numeric: tabular-nums; white-space: nowrap; }
.spark-date { font-size: 9px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

/* Search */
.search-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.search { flex: 1; background: rgba(12,12,14,0.6); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; font-size: 13px; color: var(--text-strong); outline: none; font-family: inherit; backdrop-filter: blur(8px); }
.search::placeholder { color: var(--text-muted); } .search:focus { border-color: var(--border-hover); }
.count { font-size: 11px; color: var(--text-muted); }

/* Timeline */
.timeline { position: relative; }
.month-group { margin-bottom: 8px; }
.month-header { display: flex; align-items: center; gap: 12px; padding: 12px 0; position: sticky; top: 0; background: rgba(12,12,14,0.9); backdrop-filter: blur(8px); z-index: 10; }
.month-dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid; }
.month-label { font-family: var(--serif); font-size: 15px; color: var(--text-heading); }
.month-count { font-size: 11px; color: var(--text-muted); }
.month-entries { padding-left: 4px; }
.entry-row { display: flex; align-items: stretch; cursor: pointer; position: relative; transition: background 0.1s; border-radius: 8px; margin-left: 1px; }
.entry-row:hover { background: rgba(255,255,255,0.02); } .entry-row:hover .entry-dot { transform: scale(1.4); }
.entry-line { position: absolute; left: 4px; top: 0; bottom: 0; width: 1px; background: var(--border); }
.entry-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; margin-top: 14px; margin-right: 12px; position: relative; z-index: 1; transition: all 0.15s; border: 1.5px solid; }
.entry-content { flex: 1; padding: 8px 12px 8px 0; }
.entry-top { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.entry-date { font-size: 14px; font-weight: 600; color: var(--text-strong); font-variant-numeric: tabular-nums; }
.entry-day { font-size: 12px; color: var(--text-muted); }
.entry-meta { display: flex; align-items: center; gap: 8px; margin-left: auto; font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
.meta-add { color: #34d399; font-weight: 500; }
.entry-summary { font-size: 12px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 640px) { .hero-h1 { font-size: 28px; } .feat-row-top { flex-direction: column; gap: 12px; } .entry-meta { display: none; } }
</style>
