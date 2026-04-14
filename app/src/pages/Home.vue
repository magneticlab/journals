<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import ReflectModal from '../components/ReflectModal.vue'
import ThemeSwitcher from '../components/ThemeSwitcher.vue'

const manifest = ref({ work: [], daily: [] })
const weather = ref(null)
const scrollY = ref(0)
const showReflect = ref(false)
const todayReflection = ref(null)

// Check if today already has a reflection
function loadTodayReflection() {
  const stored = JSON.parse(localStorage.getItem('reflections') || '{}')
  const today = new Date().toISOString().slice(0, 10)
  todayReflection.value = stored[today] || null
}
function onScroll() { scrollY.value = window.scrollY }

// Hero parallax: moves slower, fades out
const heroStyle = computed(() => ({
  transform: `translateY(${scrollY.value * 0.15}px)`,
  opacity: Math.max(1 - scrollY.value / 400, 0),
}))

onMounted(async () => {
  window.addEventListener('scroll', onScroll, { passive: true })
  loadTodayReflection()
  manifest.value = await (await fetch('/manifest.json')).json()
  // Fetch weather (Athens, Greece — no API key needed)
  try {
    const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=37.98&longitude=23.73&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m&timezone=auto')
    if (res.ok) weather.value = await res.json()
  } catch {}
})

// Time-based greeting
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return 'Working late'
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  if (h < 21) return 'Good evening'
  return 'Working late'
})

const todayStr = computed(() => {
  return new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
})

// Weather helpers
const weatherCodes = {
  0: { label: 'Clear', icon: '☀' },
  1: { label: 'Mostly clear', icon: '🌤' },
  2: { label: 'Partly cloudy', icon: '⛅' },
  3: { label: 'Overcast', icon: '☁' },
  45: { label: 'Foggy', icon: '🌫' },
  48: { label: 'Icy fog', icon: '🌫' },
  51: { label: 'Light drizzle', icon: '🌦' },
  53: { label: 'Drizzle', icon: '🌦' },
  55: { label: 'Heavy drizzle', icon: '🌧' },
  61: { label: 'Light rain', icon: '🌧' },
  63: { label: 'Rain', icon: '🌧' },
  65: { label: 'Heavy rain', icon: '⛈' },
  71: { label: 'Light snow', icon: '🌨' },
  73: { label: 'Snow', icon: '❄' },
  75: { label: 'Heavy snow', icon: '❄' },
  80: { label: 'Rain showers', icon: '🌦' },
  81: { label: 'Heavy showers', icon: '⛈' },
  95: { label: 'Thunderstorm', icon: '⛈' },
}

const wxLabel = computed(() => {
  if (!weather.value?.current) return null
  const code = weather.value.current.weather_code
  return weatherCodes[code] || { label: 'Unknown', icon: '🌡' }
})

const wxTemp = computed(() => weather.value?.current?.temperature_2m || null)
const wxHumidity = computed(() => weather.value?.current?.relative_humidity_2m || null)
const wxWind = computed(() => weather.value?.current?.wind_speed_10m || null)

// Consolidate days
const days = computed(() => {
  const map = new Map()
  for (const e of manifest.value.work) {
    if (!map.has(e.date)) map.set(e.date, { date: e.date, day: e.day, display: e.display })
    map.get(e.date).work = e
  }
  for (const e of manifest.value.daily) {
    if (!map.has(e.date)) map.set(e.date, { date: e.date, day: e.day, display: e.display })
    map.get(e.date).daily = e
  }
  return [...map.values()].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 21)
})

// Group by week then month
const grouped = computed(() => {
  const now = new Date()
  const groups = []
  let currentGroup = null
  for (const d of days.value) {
    const dt = new Date(d.date + 'T12:00:00')
    const diff = Math.floor((now - dt) / 86400000)
    let key, label
    if (diff < 7) { key = 'this-week'; label = 'This Week' }
    else if (diff < 14) { key = 'last-week'; label = 'Last Week' }
    else {
      const m = d.date.slice(0, 7)
      const months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
      key = m; label = `${months[parseInt(m.slice(5))]} ${m.slice(0, 4)}`
    }
    if (!currentGroup || currentGroup.key !== key) {
      currentGroup = { key, label, items: [] }
      groups.push(currentGroup)
    }
    currentGroup.items.push(d)
  }
  return groups
})

function dateNum(d) { return parseInt(d.date.slice(8)) }
function daySummary(d) {
  const parts = []
  if (d.work?.stats?.sessions) parts.push(`${d.work.stats.sessions} sessions`)
  if (d.work?.stats?.commits || d.daily?.stats?.commits) {
    const c = (d.work?.stats?.commits || 0) || (d.daily?.stats?.commits || 0)
    parts.push(`${c} commits`)
  }
  if (d.daily?.stats?.commands) parts.push(`${d.daily.stats.commands} cmds`)
  return parts.join(' · ')
}

// Paired activity chart — last 14 days
const activityBars = computed(() => {
  const workMap = new Map()
  const dailyMap = new Map()
  for (const e of manifest.value.work) workMap.set(e.date, e.stats?.commits || 0)
  for (const e of manifest.value.daily) dailyMap.set(e.date, e.stats?.commits || 0)

  const allDates = [...new Set([...workMap.keys(), ...dailyMap.keys()])].sort().reverse().slice(0, 14).reverse()
  const bars = allDates.map(date => ({
    date: date.slice(8),
    day: new Date(date + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short' }).slice(0, 2),
    work: workMap.get(date) || 0,
    daily: dailyMap.get(date) || 0,
  }))
  return bars
})
const barsMax = computed(() => Math.max(...activityBars.value.map(b => Math.max(b.work, b.daily)), 1))

onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <div class="page">
    <!-- TOP ZONE — transparent, animation visible -->
    <div class="top-zone">
      <div class="mx">
        <!-- Nav row — stays fixed, doesn't parallax -->
        <div class="nav-row">
          <router-link to="/" class="hero-logo">Journals</router-link>
          <div class="nav-right">
          <div v-if="weather" class="weather">
            <span class="wx-icon">{{ wxLabel?.icon }}</span>
            <span class="wx-temp">{{ wxTemp }}°</span>
            <span class="wx-label">{{ wxLabel?.label }}</span>
            <span class="wx-sep">·</span>
            <span class="wx-detail">{{ wxHumidity }}% humidity</span>
            <span class="wx-sep">·</span>
            <span class="wx-detail">{{ wxWind }} km/h</span>
          </div>
          <ThemeSwitcher />
          </div>
        </div>

        <!-- Hero — parallax + fade on scroll -->
        <div class="hero" :style="heroStyle">
          <p class="hero-greeting">{{ greeting }}, Alek.</p>
          <p class="hero-date">{{ todayStr }}</p>
          <button class="reflect-btn" @click="showReflect = true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
            {{ todayReflection ? 'Update Reflection' : 'Daily Reflect' }}
          </button>
        </div>

        <!-- Reflect Modal -->
        <ReflectModal v-if="showReflect" @close="showReflect = false" @submit="loadTodayReflection" />
      </div>
    </div>

    <!-- BODY ZONE — dark panel with gradient fade-in at top -->
    <div class="body-zone">
      <div class="body-fade"></div>
      <div class="body-solid">
        <!-- Cards straddling the boundary — pulled up into the fade -->
        <div class="mx cards-wrap">
          <div v-reveal class="cards">
            <router-link to="/work" class="card card-work rv">
              <div class="card-head">
                <div class="card-icon icon-work">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                </div>
                <span class="card-count">{{ manifest.work.length }}</span>
              </div>
              <h2 class="card-label">Work Journal</h2>
              <p class="card-desc">Claude Code sessions, git commits, project work.</p>
              <div class="card-bottom">
                <div class="card-stats">
                  <div class="cstat"><span class="cstat-val">{{ manifest.work.reduce((s, e) => s + (e.stats?.sessions || 0), 0) }}</span><span class="cstat-label">Sessions</span></div>
                  <div class="cstat"><span class="cstat-val">{{ manifest.work.reduce((s, e) => s + (e.stats?.commits || 0), 0) }}</span><span class="cstat-label">Commits</span></div>
                </div>
              </div>
            </router-link>

            <router-link to="/daily" class="card card-daily rv">
              <div class="card-head">
                <div class="card-icon icon-daily">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                </div>
                <span class="card-count">{{ manifest.daily.length }}</span>
              </div>
              <h2 class="card-label">Daily Journal</h2>
              <p class="card-desc">Terminal activity, file changes, development.</p>
              <div class="card-bottom">
                <div class="card-stats">
                  <div class="cstat"><span class="cstat-val">{{ manifest.daily.reduce((s, e) => s + (e.stats?.commands || 0), 0) }}</span><span class="cstat-label">Commands</span></div>
                  <div class="cstat"><span class="cstat-val">{{ manifest.daily.reduce((s, e) => s + (e.stats?.commits || 0), 0) }}</span><span class="cstat-label">Commits</span></div>
                </div>
              </div>
            </router-link>
          </div>
        </div>

        <!-- Paired Activity Chart -->
        <div v-if="activityBars.length" v-reveal class="mx activity-section">
          <div class="activity-header">
            <p class="section-label">Daily Commits — Last 14 Days</p>
            <div class="activity-legend">
              <span class="legend-item"><span class="legend-dot dot-work"></span>Work</span>
              <span class="legend-item"><span class="legend-dot dot-daily"></span>Daily</span>
            </div>
          </div>
          <div class="activity-chart">
            <div v-for="(b, i) in activityBars" :key="i" class="activity-col rv">
              <div class="bar-pair">
                <div class="bar-slot">
                  <div class="bar bar-work" :style="{ height: (b.work / barsMax * 100) + '%' }">
                    <span v-if="b.work" class="bar-val">{{ b.work }}</span>
                  </div>
                </div>
                <div class="bar-slot">
                  <div class="bar bar-daily" :style="{ height: (b.daily / barsMax * 100) + '%' }">
                    <span v-if="b.daily" class="bar-val">{{ b.daily }}</span>
                  </div>
                </div>
              </div>
              <span class="bar-day">{{ b.day }}</span>
              <span class="bar-date">{{ b.date }}</span>
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="mx timeline-wrap">
          <section class="recent-section">
            <p class="section-label">Recent Activity</p>
        <div class="timeline">
          <div v-for="group in grouped" :key="group.key" class="tl-group">
            <div class="group-header">
              <div class="group-dot"></div>
              <span class="group-label">{{ group.label }}</span>
            </div>
            <div v-reveal class="group-entries">
              <div v-for="d in group.items" :key="d.date" class="day-card rv">
                <div class="day-line"></div>
                <div class="cal-sticker">
                  <span class="cal-day">{{ d.day?.slice(0, 3) }}</span>
                  <span class="cal-num">{{ dateNum(d) }}</span>
                </div>
                <div class="day-content">
                  <div class="day-cols">
                    <router-link v-if="d.work" :to="`/work/${d.date}`" class="day-col col-work">
                      <div class="col-head"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg><span class="col-label">Work</span></div>
                      <p class="col-summary">{{ d.work.summary }}</p>
                      <div class="col-meta" v-if="d.work.stats"><span v-if="d.work.stats.sessions">{{ d.work.stats.sessions }}s</span><span v-if="d.work.stats.commits">{{ d.work.stats.commits }}c</span></div>
                    </router-link>
                    <div v-else class="day-col col-empty"><span class="empty-label">—</span></div>
                    <router-link v-if="d.daily" :to="`/daily/${d.date}`" class="day-col col-daily">
                      <div class="col-head"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg><span class="col-label">Daily</span></div>
                      <p class="col-summary">{{ d.daily.summary }}</p>
                      <div class="col-meta" v-if="d.daily.stats"><span v-if="d.daily.stats.commands">{{ d.daily.stats.commands }} cmd</span><span v-if="d.daily.stats.commits">{{ d.daily.stats.commits }}c</span></div>
                    </router-link>
                    <div v-else class="day-col col-empty"><span class="empty-label">—</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; position: relative; z-index: 1; }
.mx { max-width: 880px; margin: 0 auto; padding: 0 24px; }

/* TOP ZONE — transparent, animation shows through */
.top-zone { padding: 48px 0 0; }

/* Nav row — same height as inner pages */
.nav-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px; min-height: 36px; }

/* Hero */
.hero { margin-bottom: 0; padding-bottom: 120px; will-change: transform, opacity; }
.hero-logo { font-family: var(--serif); font-size: 20px; font-weight: 400; color: var(--text-heading); }
.nav-right { display: flex; align-items: center; gap: 8px; }
.weather {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--text-muted);
  background: rgba(12,12,14,0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border); border-radius: 10px; padding: 6px 14px;
}
.wx-icon { font-size: 16px; }
.wx-temp { font-weight: 600; color: var(--text-strong); font-size: 14px; }
.wx-label { color: var(--text); }
.wx-sep { color: var(--border-hover); }
.wx-detail { color: var(--text-muted); }

.hero-greeting { font-family: var(--serif); font-size: 42px; font-weight: 400; color: var(--text-heading); line-height: 1.2; margin-top: 8px; }
.hero-date { font-size: 15px; color: var(--text-muted); margin-top: 10px; }
.reflect-btn {
  display: inline-flex; align-items: center; gap: 8px;
  margin-top: 20px; padding: 10px 20px; border-radius: 10px;
  border: 1px solid rgba(52,211,153,0.2);
  background: rgba(52,211,153,0.08);
  color: #34d399; font-size: 13px; font-weight: 600;
  font-family: inherit; cursor: pointer;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  transition: all 0.2s var(--ease-spring);
}
.reflect-btn:hover { background: rgba(52,211,153,0.15); border-color: rgba(52,211,153,0.35); }

/* BODY ZONE — soft gradient, no hard edge */
.body-zone {
  position: relative;
  background: linear-gradient(to bottom, transparent 0%, #0c0c0e 150px);
  margin-top: -80px;
  padding-top: 80px;
  min-height: 100vh;
}
.body-fade { display: none; }
.body-solid {
  position: relative; z-index: 1;
  padding-bottom: 64px;
}

/* Cards — pulled up into the fade zone */
.cards-wrap { position: relative; margin-top: -60px; z-index: 2; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 56px; }
.card {
  border-radius: 14px; padding: 24px; transition: all 0.4s var(--ease-spring); display: block;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
}
.card-work {
  background: linear-gradient(135deg, rgba(99,149,255,0.1) 0%, rgba(12,12,14,0.85) 50%);
  border: 1px solid rgba(99,149,255,0.2);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
}
.card-work:hover { border-color: rgba(99,149,255,0.4); box-shadow: 0 8px 28px rgba(0,0,0,0.4), 0 0 24px rgba(99,149,255,0.08); }
.card-daily {
  background: linear-gradient(135deg, rgba(52,211,153,0.1) 0%, rgba(12,12,14,0.85) 50%);
  border: 1px solid rgba(52,211,153,0.2);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
}
.card-daily:hover { border-color: rgba(52,211,153,0.4); box-shadow: 0 8px 28px rgba(0,0,0,0.4), 0 0 24px rgba(52,211,153,0.08); }
.card-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px; }
.card-icon { display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 10px; }
.icon-work { background: rgba(99,149,255,0.12); color: #6395ff; }
.icon-daily { background: rgba(52,211,153,0.12); color: #34d399; }
.card-count { font-size: 12px; font-weight: 600; color: var(--text-muted); background: var(--bg-elevated); padding: 3px 10px; border-radius: 6px; }
.card-label { font-family: var(--serif); font-size: 24px; font-weight: 400; color: var(--text-heading); margin-bottom: 4px; }
.card-desc { font-size: 13px; color: var(--text-muted); line-height: 1.5; margin-bottom: 20px; }
.card-bottom { display: flex; align-items: flex-end; justify-content: space-between; padding-top: 16px; border-top: 1px solid var(--border); }
.card-stats { display: flex; gap: 24px; }
.cstat { display: flex; flex-direction: column; gap: 2px; }
.cstat-val { font-size: 18px; font-weight: 700; color: var(--text-heading); font-variant-numeric: tabular-nums; }
.cstat-label { font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); }
/* Paired Activity Chart */
.activity-section { margin-bottom: 48px; }
.activity-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.activity-legend { display: flex; gap: 14px; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--text-muted); }
.legend-dot { width: 8px; height: 8px; border-radius: 2px; }
.dot-work { background: #6395ff; }
.dot-daily { background: #34d399; }

.activity-chart {
  display: flex; gap: 4px; align-items: flex-end; height: 100px;
  padding: 0 4px;
}
.activity-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 0; }
.bar-pair { display: flex; gap: 2px; align-items: flex-end; height: 72px; width: 100%; }
.bar-slot { flex: 1; height: 100%; display: flex; align-items: flex-end; justify-content: center; }
.bar {
  width: 100%; min-height: 2px; border-radius: 3px 3px 1px 1px;
  position: relative; transition: height 0.5s var(--ease-spring);
}
.bar.bar-work { background: rgba(99,149,255,0.6); }
.bar.bar-daily { background: rgba(52,211,153,0.6); }
.bar-val {
  position: absolute; top: -15px; left: 50%; transform: translateX(-50%);
  font-size: 9px; font-weight: 600; color: var(--text-strong);
  font-variant-numeric: tabular-nums; white-space: nowrap;
}
.bar-day { font-size: 9px; color: var(--text-muted); text-transform: uppercase; }
.bar-date { font-size: 9px; color: var(--border-hover); font-variant-numeric: tabular-nums; }

/* Timeline */
.timeline-wrap { position: relative; }
.timeline-wrap::after {
  content: ''; position: sticky; bottom: 0; display: block;
  height: 80px; margin-top: -80px; pointer-events: none;
  background: linear-gradient(to bottom, transparent, #0c0c0e);
}
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 16px; }
.timeline { position: relative; }
.tl-group { margin-bottom: 4px; }
.group-header { display: flex; align-items: center; gap: 12px; padding: 10px 0; position: sticky; top: 0; background: rgba(12,12,14,0.9); backdrop-filter: blur(8px); z-index: 10; }
.group-dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--border-hover); background: var(--bg); flex-shrink: 0; }
.group-label { font-family: var(--serif); font-size: 15px; color: var(--text-heading); }

.group-entries { padding-left: 4px; }
.day-card { display: flex; align-items: flex-start; position: relative; margin-left: 1px; gap: 0; }
.day-line { position: absolute; left: 22px; top: 0; bottom: 0; width: 1px; background: var(--border); }
.cal-sticker {
  width: 44px; flex-shrink: 0; margin-top: 10px; margin-right: 12px;
  display: flex; flex-direction: column; align-items: center;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  padding: 6px 4px; position: relative; z-index: 1; transition: border-color 0.15s;
}
.day-card:hover .cal-sticker { border-color: var(--border-hover); }
.cal-day { font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); }
.cal-num { font-size: 18px; font-weight: 700; color: var(--text-heading); font-variant-numeric: tabular-nums; line-height: 1.1; }

.day-content {
  flex: 1; margin: 6px 0;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px;
  overflow: hidden; transition: border-color 0.15s;
}
.day-card:hover .day-content { border-color: var(--border-hover); }
.day-cols { display: grid; grid-template-columns: 1fr 1fr; }
.day-col { padding: 12px 14px; transition: background 0.1s; display: flex; flex-direction: column; gap: 6px; }
.day-col:first-child { border-right: 1px solid var(--border); }
.day-col:hover { background: var(--bg-elevated); }
.col-head { display: flex; align-items: center; gap: 5px; }
.col-work .col-head { color: #6395ff; }
.col-daily .col-head { color: #34d399; }
.col-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.col-summary { font-size: 11px; color: var(--text-muted); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.col-meta { display: flex; gap: 8px; font-size: 10px; color: var(--text-muted); font-variant-numeric: tabular-nums; margin-top: auto; }
.col-empty { display: flex; align-items: center; justify-content: center; min-height: 60px; }
.empty-label { font-size: 11px; color: var(--border-hover); }

@media (max-width: 640px) {
  .cards { grid-template-columns: 1fr; }
  .day-cols { grid-template-columns: 1fr; }
  .day-col:first-child { border-right: none; border-bottom: 1px solid var(--border); }
  .nav-row { flex-direction: column; align-items: flex-start; gap: 12px; }
  .hero-greeting { font-size: 28px; }
  .cards-wrap { margin-top: -20px; }
  .body-fade { height: 80px; }
}
</style>
