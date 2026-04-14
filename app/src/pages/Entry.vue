<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import CalendarPicker from '../components/CalendarPicker.vue'
import RadarChart from '../components/RadarChart.vue'

const props = defineProps({ journal: String, date: String })
const router = useRouter()
const data = ref(null)
const manifest = ref({ work: [], daily: [] })
const loading = ref(true)
const weather = ref(null)
const showTimeline = ref(false)
const perfView = ref('radar') // 'radar' or 'bars'
const reflection = ref(null)

function loadReflection() {
  const stored = JSON.parse(localStorage.getItem('reflections') || '{}')
  reflection.value = stored[props.date] || null
}

// Extract keywords/themes from text
function extractThemes(text) {
  if (!text) return []
  const t = text.toLowerCase()
  const themes = []
  const patterns = [
    { words: ['ship', 'launch', 'deploy', 'release', 'publish'], label: 'Shipping', icon: '🚀' },
    { words: ['design', 'figma', 'ui', 'ux', 'layout', 'visual'], label: 'Design', icon: '🎨' },
    { words: ['bug', 'fix', 'error', 'broken', 'issue', 'debug'], label: 'Problem Solving', icon: '🔧' },
    { words: ['learn', 'discover', 'realize', 'understand', 'insight'], label: 'Learning', icon: '📚' },
    { words: ['team', 'collaborat', 'discuss', 'meeting', 'sync', 'review'], label: 'Collaboration', icon: '🤝' },
    { words: ['refactor', 'clean', 'restructur', 'organiz', 'simplif'], label: 'Refinement', icon: '✨' },
    { words: ['plan', 'strateg', 'roadmap', 'priorit', 'decision'], label: 'Strategy', icon: '🧭' },
    { words: ['focus', 'distract', 'context switch', 'interrupt'], label: 'Focus', icon: '🎯' },
    { words: ['energy', 'tired', 'exhaust', 'rest', 'sleep', 'burnout'], label: 'Wellbeing', icon: '💪' },
    { words: ['progress', 'momentum', 'velocity', 'productive'], label: 'Momentum', icon: '⚡' },
    { words: ['stuck', 'block', 'frustrat', 'difficult', 'challeng'], label: 'Friction', icon: '🧱' },
    { words: ['creativ', 'idea', 'concept', 'experiment', 'explor'], label: 'Creative', icon: '💡' },
    { words: ['component', 'system', 'token', 'architecture'], label: 'Systems', icon: '⬡' },
    { words: ['commit', 'code', 'implement', 'build', 'develop'], label: 'Building', icon: '🔨' },
  ]
  for (const p of patterns) {
    if (p.words.some(w => t.includes(w))) themes.push(p)
  }
  return themes.slice(0, 3)
}

const reflectEval = computed(() => {
  if (!reflection.value) return null
  const { energy, focus, mood } = reflection.value.scores
  const avg = reflection.value.average
  const tags = []
  const insights = []

  // Overall assessment
  if (avg >= 8) { tags.push({ label: 'Peak Day', color: '#34d399' }) }
  else if (avg >= 6) { tags.push({ label: 'Solid Day', color: '#fbbf24' }) }
  else if (avg >= 4) { tags.push({ label: 'Mixed Day', color: '#fb923c' }) }
  else { tags.push({ label: 'Recovery Needed', color: '#f87171' }) }

  // Score patterns
  if (energy >= 8 && focus >= 8 && mood >= 8) { tags.push({ label: 'Flow State', color: '#34d399' }) }
  else if (energy >= 8 && focus < 6) { tags.push({ label: 'Energy → Focus Gap', color: '#fb923c' }) }
  else if (focus >= 8 && energy < 6) { tags.push({ label: 'Pushing Through', color: '#fbbf24' }) }
  if (focus >= 9) tags.push({ label: 'Deep Focus', color: '#34d399' })
  if (energy <= 4) tags.push({ label: 'Low Battery', color: '#f87171' })
  if (mood <= 4 && energy <= 4) tags.push({ label: 'Burnout Risk', color: '#f87171' })

  // Strongest and weakest
  const scores = [['Energy', energy], ['Focus', focus], ['Mood', mood]]
  const strongest = scores.reduce((a, b) => b[1] > a[1] ? b : a)
  const weakest = scores.reduce((a, b) => b[1] < a[1] ? b : a)
  if (strongest[1] !== weakest[1]) {
    insights.push(`${strongest[0]} was your strongest area today at ${strongest[1]}/10, while ${weakest[0].toLowerCase()} scored ${weakest[1]}/10.`)
  }

  // Win analysis
  const winThemes = extractThemes(reflection.value.win)
  if (winThemes.length) {
    insights.push(`Your win centered on ${winThemes.map(t => t.label.toLowerCase()).join(' and ')} — keep this momentum going.`)
  }

  // Improve analysis
  const improveThemes = extractThemes(reflection.value.improve)
  if (improveThemes.length) {
    insights.push(`Areas to watch: ${improveThemes.map(t => t.label.toLowerCase()).join(', ')}. Set a specific action for tomorrow.`)
  }

  // Score-based insight
  if (avg >= 7) {
    insights.push('Above-average day overall. Document what worked so you can replicate these conditions.')
  } else if (avg <= 4) {
    insights.push('Below your baseline. Identify the root cause — was it external factors or internal state?')
  }

  return {
    tags: tags.slice(0, 4),
    insights: insights.slice(0, 3),
    winThemes,
    improveThemes,
  }
})
const scrollY = ref(0)
function onScroll() { scrollY.value = window.scrollY }

const heroStyle = computed(() => ({
  transform: `translateY(${scrollY.value * 0.15}px)`,
  opacity: Math.max(1 - scrollY.value / 400, 0),
}))

onMounted(async () => {
  window.addEventListener('scroll', onScroll, { passive: true })
  manifest.value = await (await fetch('/manifest.json')).json()
  loadEntry()
  loadReflection()
  try {
    const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=37.98&longitude=23.73&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m&timezone=auto')
    if (res.ok) weather.value = await res.json()
  } catch {}
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))

watch(() => props.date, () => { loadEntry(); loadReflection() })
async function loadEntry() {
  // Don't clear data — keep old content visible to prevent flicker
  try {
    const res = await fetch(`/entries/${props.journal}/${props.date}.json`)
    data.value = res.ok ? await res.json() : null
  } catch { data.value = null }
  loading.value = false
}

const entries = computed(() => manifest.value[props.journal] || [])
const dates = computed(() => entries.value.map(e => e.date))
const idx = computed(() => dates.value.indexOf(props.date))
const hasPrev = computed(() => idx.value < dates.value.length - 1)
const hasNext = computed(() => idx.value > 0)
function goToPrev() { if (hasPrev.value) router.push(`/${props.journal}/${dates.value[idx.value + 1]}`) }
function goToNext() { if (hasNext.value) router.push(`/${props.journal}/${dates.value[idx.value - 1]}`) }
function goTo(e) { if (typeof e === 'string') router.push(`/${props.journal}/${e}`); else router.push(`/${props.journal}/${e.target.value}`) }

const isWork = computed(() => props.journal === 'work')
const today = computed(() => new Date().toISOString().slice(0, 10))
const isToday = computed(() => props.date === today.value)
const hasTodayEntry = computed(() => dates.value.includes(today.value))
function goToday() { if (hasTodayEntry.value) router.push(`/${props.journal}/${today.value}`) }
const brand = computed(() => isWork.value ? '#6395ff' : '#34d399')

// Check if the other journal has an entry for this date
const hasOtherJournal = computed(() => {
  const other = isWork.value ? manifest.value.daily : manifest.value.work
  return other.some(e => e.date === props.date)
})

const themeIcons = { 'Design System': '⬡', 'Design & Layout': '◫', 'Page Building': '▦', 'Animation & Effects': '✦', 'Bug Fixes': '⚠', 'Git & Deployment': '⎇', 'Version Iteration': '↻', 'Refactoring': '⟲', 'Content & Copy': '¶', 'Planning & Strategy': '◈', 'General Development': '⌘', 'Git': '⎇', 'Claude Code': '◉', 'Navigation': '≡', 'File Inspection': '◧', 'Package Management': '⬢', 'Homebrew': '⚗', 'Remote': '⚡', 'GitHub CLI': '⎇', 'File Operations': '◧', 'Other': '◆', 'Docker': '◎', 'Python': '◉', 'HTTP': '◎' }
function scoreColor(s) { if (s >= 75) return '#34d399'; if (s >= 50) return '#fbbf24'; if (s >= 25) return '#fb923c'; return '#f87171' }

function ringScoreColor(s) {
  const stops = [[0,[248,113,113]],[35,[251,146,60]],[55,[251,191,36]],[100,[52,211,153]]]
  let lo = stops[0], hi = stops[stops.length-1]
  for (let i = 0; i < stops.length-1; i++) { if (s >= stops[i][0] && s <= stops[i+1][0]) { lo = stops[i]; hi = stops[i+1]; break } }
  const t = (s - lo[0]) / (hi[0] - lo[0] || 1)
  const r = Math.round(lo[1][0]+(hi[1][0]-lo[1][0])*t), g = Math.round(lo[1][1]+(hi[1][1]-lo[1][1])*t), b = Math.round(lo[1][2]+(hi[1][2]-lo[1][2])*t)
  return `rgb(${r},${g},${b})`
}
const genTime = computed(() => { if (!data.value?.generatedAt) return ''; return new Date(data.value.generatedAt).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) })
const activeHours = computed(() => { const tr = data.value?.stats?.timeRange; if (!tr) return null; const p = tr.split('–'); if (p.length !== 2) return null; const [h1,m1] = p[0].split(':').map(Number); const [h2,m2] = p[1].split(':').map(Number); const mins = (h2*60+m2)-(h1*60+m1); if (mins <= 0) return null; const h = Math.floor(mins/60); const m = mins%60; return h > 0 ? `${h}h ${m}m` : `${m}m` })
const summaryLine = computed(() => { if (!data.value) return ''; const s = data.value.stats; const parts = []; if (isWork.value) { if (s?.sessions) parts.push(`${s.sessions} sessions`); if (s?.commits) parts.push(`${s.commits} commits`); if (s?.linesAdded) parts.push(`+${s.linesAdded.toLocaleString()} lines`); if (activeHours.value) parts.push(activeHours.value+' active') } else { if (s?.commands) parts.push(`${s.commands} commands`); if (s?.commits) parts.push(`${s.commits} commits`) }; return parts.join(' · ') })

const wxCodes = { 0: { l: 'Clear', i: '☀' }, 1: { l: 'Mostly clear', i: '🌤' }, 2: { l: 'Partly cloudy', i: '⛅' }, 3: { l: 'Overcast', i: '☁' }, 45: { l: 'Foggy', i: '🌫' }, 51: { l: 'Drizzle', i: '🌦' }, 61: { l: 'Rain', i: '🌧' }, 63: { l: 'Rain', i: '🌧' }, 80: { l: 'Showers', i: '🌦' }, 95: { l: 'Storm', i: '⛈' } }
const wx = computed(() => { if (!weather.value?.current) return null; const c = weather.value.current; const w = wxCodes[c.weather_code] || { l: '—', i: '🌡' }; return { ...w, temp: c.temperature_2m, hum: c.relative_humidity_2m, wind: c.wind_speed_10m } })
</script>

<template>
  <div class="page">
    <!-- Top zone -->
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
        <div v-if="data" class="hero" :style="heroStyle">
          <div class="hero-title-row">
            <button @click="goToPrev" :disabled="!hasPrev" :class="['arrow-btn', { disabled: !hasPrev }]">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <h1 class="hero-h1">{{ data.day }}, {{ data.display }}</h1>
            <button @click="goToNext" :disabled="!hasNext" :class="['arrow-btn', { disabled: !hasNext }]">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
            </button>
            <CalendarPicker :modelValue="date" @update:modelValue="goTo" :availableDates="dates" :brandColor="brand" />
            <button v-if="!isToday && hasTodayEntry" class="today-btn" @click="goToday">Today</button>
          </div>
          <p class="hero-sub">{{ summaryLine }}</p>

          <!-- Journal tabs — switch between work/daily for this day -->
          <div class="journal-tabs">
            <router-link :to="`/work/${date}`" :class="['jtab', { active: journal === 'work' }]">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
              Work
            </router-link>
            <router-link v-if="hasOtherJournal || journal === 'daily'" :to="`/daily/${date}`" :class="['jtab', { active: journal === 'daily' }]">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              Daily
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Body zone -->
    <div class="body-zone">
      <div v-if="loading" class="mx empty">Loading...</div>
      <div v-else-if="!data" class="mx empty">No entry for this date.</div>
      <div v-else class="mx body">

        <!-- Went Right / Could Be Better -->
        <div v-if="data.wentRight || data.couldBeBetter" v-reveal class="duo-grid">
          <div v-if="data.wentRight" class="duo-card duo-green rv"><div class="duo-accent accent-green"></div><div class="duo-icon">✓</div><div><p class="duo-label">Went Right</p><p class="duo-text">{{ data.wentRight }}</p></div></div>
          <div v-if="data.couldBeBetter" class="duo-card duo-red rv"><div class="duo-accent accent-red"></div><div class="duo-icon duo-icon-red">!</div><div><p class="duo-label">Could Be Better</p><p class="duo-text">{{ data.couldBeBetter }}</p></div></div>
        </div>

        <!-- Performance -->
        <section v-if="isWork && data.metrics" v-reveal class="section">
          <div class="perf-header">
            <p class="section-label" :style="{ color: brand }">Performance</p>
            <div class="perf-toggle">
              <button :class="{ active: perfView === 'radar' }" @click="perfView = 'radar'">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5"/></svg>
              </button>
              <button :class="{ active: perfView === 'bars' }" @click="perfView = 'bars'">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="5" width="4" height="16" rx="1"/><rect x="17" y="8" width="4" height="13" rx="1"/></svg>
              </button>
            </div>
          </div>

          <!-- View A: Radar + rings -->
          <div v-show="perfView === 'radar'" class="perf-card">
            <div class="perf-radar">
              <RadarChart :metrics="data.metrics" :brandColor="brand" :size="280" />
            </div>
            <div class="perf-rings">
              <div v-for="(m, key) in data.metrics" :key="key" class="ring-item">
                <div class="ring-wrap">
                  <div class="ring-bg"></div>
                  <div class="ring-fill" :style="{ background: `conic-gradient(from 0deg, #f87171 0%, #fb923c ${m.score * 0.3}%, #fbbf24 ${m.score * 0.55}%, #34d399 ${m.score * 0.9}%, transparent ${m.score}%, transparent 100%)` }"></div>
                  <span class="ring-score" :style="{ color: ringScoreColor(m.score) }">{{ m.score }}</span>
                </div>
                <span class="ring-name">{{ m.label }}</span>
              </div>
            </div>
          </div>

          <!-- View B: Horizontal bars -->
          <div v-show="perfView === 'bars'" class="perf-bars-card">
            <div v-for="(m, key) in data.metrics" :key="key" class="bar-row">
              <div class="bar-info">
                <span class="bar-label">{{ m.label }}</span>
                <span class="bar-score" :style="{ color: ringScoreColor(m.score) }">{{ m.score }}</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: m.score + '%', background: `linear-gradient(90deg, #f87171, #fb923c 30%, #fbbf24 55%, ${ringScoreColor(m.score)})` }"></div>
              </div>
            </div>
          </div>
        </section>

        <!-- What I Did — narrative summaries -->
        <section v-if="isWork && data.whatIDid?.length" v-reveal class="section">
          <p class="section-label">What I Did</p>
          <ul class="narrative-list">
            <li v-for="(item, i) in data.whatIDid" :key="i" class="narrative-item rv">
              <span class="narrative-dot" :style="{ background: brand }"></span>
              <span class="narrative-text">{{ item }}</span>
            </li>
          </ul>
        </section>

        <!-- Continued From Yesterday + Roadblocks -->
        <div v-if="isWork && (data.continuedFromYesterday?.length || data.roadblocks?.length)" v-reveal class="cont-grid">
          <section v-if="data.continuedFromYesterday?.length" class="cont-card rv">
            <p class="section-label">Continued From Yesterday</p>
            <ul class="cont-list">
              <li v-for="(item, i) in data.continuedFromYesterday" :key="i">
                <span class="cont-dot"></span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </section>
          <section v-if="data.roadblocks?.length" class="cont-card rv">
            <p class="section-label" style="color: var(--amber)">Roadblocks</p>
            <ul class="cont-list">
              <li v-for="(item, i) in data.roadblocks" :key="i">
                <span class="cont-dot dot-amber"></span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </section>
        </div>

        <!-- Insights -->
        <section v-if="isWork && data.insights?.length" v-reveal class="section section-tint" style="--tint: rgba(99,149,255,0.04)">
          <p class="section-label" :style="{ color: brand }">Insights</p>
          <ul class="insights-list">
            <li v-for="(item, i) in data.insights" :key="i" class="insight-item rv">
              <span class="insight-dot" :style="{ background: brand }"></span>
              <span class="insight-text">{{ item }}</span>
            </li>
          </ul>
        </section>

        <!-- Focus Areas / Terminal Activity -->
        <section v-if="(isWork && data.themes && Object.keys(data.themes).length) || (!isWork && data.categories && Object.keys(data.categories).length)" v-reveal class="section section-tint" :style="{ '--tint': brand + '04' }">
          <p class="section-label" :style="{ color: brand }">{{ isWork ? 'Focus Areas' : 'Terminal Activity' }}</p>
          <div class="theme-grid"><div v-for="(count, name) in (isWork ? data.themes : data.categories)" :key="name" class="theme-card rv"><span class="theme-icon">{{ themeIcons[name] || '◆' }}</span><div class="theme-body"><span class="theme-name">{{ name }}</span><span class="theme-count">{{ count }} interactions</span></div></div></div>
        </section>

        <!-- Activity by Hour -->
        <section v-if="!isWork && data.activityByHour && Object.keys(data.activityByHour).length" v-reveal class="section">
          <p class="section-label" :style="{ color: brand }">Activity by Hour</p>
          <div class="hours-card"><div v-for="(count, hour) in data.activityByHour" :key="hour" class="hour-row"><span class="hour-label">{{ hour }}:00</span><div class="hour-track"><div class="hour-fill" :style="{ width: Math.min(count / Math.max(...Object.values(data.activityByHour)) * 100, 100) + '%', background: brand }"></div></div><span class="hour-n">{{ count }}</span></div></div>
        </section>

        <!-- Volume -->
        <section v-if="isWork && (data.stats?.linesAdded || data.stats?.linesRemoved)" v-reveal class="section section-tint" style="--tint: rgba(52,211,153,0.04)">
          <p class="section-label">Code Volume</p>
          <div class="vol-card"><div class="vol-accent accent-green"></div><div class="vol-bar"><div class="vol-add-bar" :style="{ flex: data.stats.linesAdded || 1 }"></div><div class="vol-del-bar" :style="{ flex: data.stats.linesRemoved || 1 }"></div></div><div class="vol-labels"><span class="vol-add">+{{ (data.stats.linesAdded||0).toLocaleString() }}</span><span class="vol-del">-{{ (data.stats.linesRemoved||0).toLocaleString() }}</span><span class="vol-files">{{ data.stats.filesChanged||0 }} files</span></div></div>
        </section>

        <!-- Projects -->
        <section v-if="isWork && data.projectsWip?.length" v-reveal class="section">
          <p class="section-label">Projects</p>
          <div class="project-tags"><div v-for="(p, i) in data.projectsWip" :key="i" class="project-tag rv"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>{{ p }}</div></div>
        </section>

        <!-- Expandable Activity Timeline -->
        <section v-if="isWork && data.activityTimeline?.length" class="section">
          <button class="timeline-toggle" @click="showTimeline = !showTimeline">
            <svg :class="['toggle-chevron', { open: showTimeline }]" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
            <span>Explore Activity</span>
            <span class="toggle-count">{{ data.activityTimeline.length }} items</span>
          </button>
          <Transition name="expand">
            <div v-if="showTimeline" class="timeline-list">
              <div v-for="(item, i) in data.activityTimeline" :key="i" class="tl-item">
                <span class="tl-num">{{ i + 1 }}</span>
                <span class="tl-text">{{ item }}</span>
              </div>
            </div>
          </Transition>
        </section>

        <!-- Docs -->
        <section v-if="isWork && data.docsCreated?.length" v-reveal class="section section-tint" style="--tint: rgba(167,139,250,0.04)">
          <p class="section-label" style="color: var(--purple)">Docs Created</p>
          <div class="docs-list"><div v-for="(doc, i) in data.docsCreated" :key="i" class="doc-row rv"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg><span class="doc-title">{{ doc.title }}</span><span class="doc-leader"></span><span class="doc-desc">{{ doc.description }}</span></div></div>
        </section>

        <!-- Commands -->
        <section v-if="!isWork && data.notableCommands?.length" v-reveal class="section">
          <p class="section-label" :style="{ color: brand }">Notable Commands</p>
          <div class="cmd-card"><div v-for="(cmd, i) in data.notableCommands.slice(0, 20)" :key="i" class="cmd-row rv"><span class="cmd-time">{{ cmd.time }}</span><code class="cmd-text">{{ cmd.command }}</code></div></div>
        </section>

        <!-- Git -->
        <section v-if="data.gitActivity?.length" v-reveal class="section section-tint" style="--tint: rgba(52,211,153,0.03)">
          <p class="section-label" style="color: var(--green)">Git Activity</p>
          <div v-for="repo in data.gitActivity" :key="repo.repo" class="git-card rv">
            <div class="git-accent"></div>
            <div class="git-inner"><div class="repo-head"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="1.5"><path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg><span class="repo-name">{{ repo.repo }}</span><span v-if="repo.stat" class="repo-stat">{{ repo.stat }}</span></div><div class="commits"><div v-for="c in repo.commits" :key="c.hash" class="commit"><code class="chash">{{ c.hash }}</code><span class="ctime">{{ c.time }}</span><span class="cleader"></span><span class="cmsg">{{ c.message }}</span></div></div></div>
          </div>
        </section>

        <!-- Files -->
        <section v-if="!isWork && data.fileGroups && Object.keys(data.fileGroups).length" v-reveal class="section">
          <p class="section-label">Files Modified</p>
          <div class="files-card"><div v-for="(files, dir) in data.fileGroups" :key="dir" class="fgroup rv"><p class="fdir"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>{{ dir }}/ <span class="fcount">({{ files.length }})</span></p><p v-for="f in files" :key="f" class="fpath">{{ f }}</p></div></div>
        </section>

        <!-- Daily Reflection -->
        <section v-if="reflection" v-reveal class="section">
          <p class="section-label" style="color: #34d399">Daily Reflection</p>
          <div class="reflect-card">
            <!-- Evaluation: insights + tags -->
            <div v-if="reflectEval" class="reflect-eval">
              <div class="eval-tags">
                <span v-for="t in reflectEval.tags" :key="t.label" class="eval-tag" :style="{ color: t.color, borderColor: t.color + '30', background: t.color + '10' }">{{ t.label }}</span>
              </div>
              <ul class="eval-insights">
                <li v-for="(ins, i) in reflectEval.insights" :key="i">{{ ins }}</li>
              </ul>
            </div>

            <!-- Scores: 3 small on left, average large on right -->
            <div class="reflect-scores">
              <div class="rscores-left">
                <div class="rscore" v-for="(val, key) in reflection.scores" :key="key">
                  <div class="rscore-ring">
                    <svg width="48" height="48" viewBox="0 0 48 48">
                      <circle cx="24" cy="24" r="20" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="3" />
                      <circle cx="24" cy="24" r="20" fill="none" stroke-width="3" stroke-linecap="round" :stroke="ringScoreColor(val * 10)" :stroke-dasharray="`${val * 12.566} 200`" transform="rotate(-90 24 24)" />
                    </svg>
                    <span class="rscore-num" :style="{ color: ringScoreColor(val * 10) }">{{ val }}</span>
                  </div>
                  <span class="rscore-label">{{ key }}</span>
                </div>
              </div>
              <div class="rscore-avg">
                <div class="rscore-ring rscore-ring-lg">
                  <svg width="72" height="72" viewBox="0 0 72 72">
                    <circle cx="36" cy="36" r="30" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="4" />
                    <circle cx="36" cy="36" r="30" fill="none" stroke-width="4" stroke-linecap="round" :stroke="ringScoreColor(reflection.average * 10)" :stroke-dasharray="`${reflection.average * 18.85} 250`" transform="rotate(-90 36 36)" />
                  </svg>
                  <span class="rscore-num rscore-num-lg" :style="{ color: ringScoreColor(reflection.average * 10) }">{{ reflection.average }}</span>
                </div>
                <span class="rscore-label">Average</span>
              </div>
            </div>

            <!-- Text responses with extracted themes -->
            <div class="reflect-text" v-if="reflection.win || reflection.improve">
              <div v-if="reflection.win" class="rtext-block">
                <div class="rtext-head">
                  <p class="rtext-label">Biggest Win</p>
                  <div class="rtext-themes" v-if="reflectEval?.winThemes?.length">
                    <span v-for="t in reflectEval.winThemes" :key="t.label" class="rtext-theme">{{ t.icon }} {{ t.label }}</span>
                  </div>
                </div>
                <p class="rtext-content">{{ reflection.win }}</p>
              </div>
              <div v-if="reflection.improve" class="rtext-block">
                <div class="rtext-head">
                  <p class="rtext-label" style="color: var(--amber)">What to Improve</p>
                  <div class="rtext-themes" v-if="reflectEval?.improveThemes?.length">
                    <span v-for="t in reflectEval.improveThemes" :key="t.label" class="rtext-theme">{{ t.icon }} {{ t.label }}</span>
                  </div>
                </div>
                <p class="rtext-content">{{ reflection.improve }}</p>
              </div>
            </div>
          </div>
        </section>
      </div>
      <div v-if="data?.generatedAt" class="footer"><p class="footer-text">Generated {{ genTime }}</p></div>
    </div>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; position: relative; z-index: 1; }
.mx { max-width: 880px; margin: 0 auto; padding-left: 24px; padding-right: 24px; }

/* Top zone — above body-zone so calendar dropdown isn't hidden */
.top-zone { padding: 48px 0 0; position: relative; z-index: 10; }
.nav-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px; min-height: 36px; }
.hero-logo { font-family: var(--serif); font-size: 20px; color: var(--text-heading); }
.hero-logo:hover { color: var(--text-muted); }
.weather { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); background: rgba(12,12,14,0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid var(--border); border-radius: 10px; padding: 6px 14px; }
.wx-i { font-size: 16px; } .wx-t { font-weight: 600; color: var(--text-strong); font-size: 14px; } .wx-l { color: var(--text); }

/* Hero */
.hero { padding-bottom: 48px; will-change: transform, opacity; }
.hero-title-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.hero-h1 { font-family: var(--serif); font-size: 36px; font-weight: 400; color: var(--text-heading); flex: 1; }
.hero-sub { font-size: 14px; color: var(--text-muted); margin-bottom: 16px; }

/* Arrow buttons */
.arrow-btn {
  display: flex; align-items: center; justify-content: center;
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
  border: 1px solid var(--border); background: rgba(12,12,14,0.7);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  color: var(--text); cursor: pointer;
  transition: all 0.2s var(--ease-spring);
}
.arrow-btn:hover { border-color: var(--border-hover); color: var(--text-heading); background: rgba(12,12,14,0.85); }
.arrow-btn.disabled { color: var(--border); cursor: not-allowed; opacity: 0.4; }

.today-btn {
  padding: 8px 14px; border-radius: 8px; border: none;
  background: rgba(52,211,153,0.15); color: #34d399;
  font-size: 12px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s var(--ease-spring);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.today-btn:hover { background: rgba(52,211,153,0.25); }

/* Journal tabs — switch work/daily for this day */
.journal-tabs { display: flex; gap: 4px; }
.jtab {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 16px; border-radius: 8px;
  font-size: 13px; font-weight: 500;
  color: var(--text-muted); transition: all 0.15s;
  background: rgba(255,255,255,0.03);
}
.jtab:hover { color: var(--text-strong); background: rgba(255,255,255,0.06); }
.jtab.active { color: var(--text-heading); background: rgba(255,255,255,0.08); }

/* Body zone — below top-zone in stacking */
.body-zone { position: relative; z-index: 5; background: linear-gradient(to bottom, transparent 0%, #0c0c0e 120px); padding-top: 20px; min-height: 100vh; }
.body { padding-bottom: 64px; }
.empty { padding: 80px 24px; text-align: center; font-size: 14px; color: var(--text-muted); }

/* Sections */
.section { margin-bottom: 32px; }
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 12px; }

/* Section tinting */
.section-tint { background: var(--tint, transparent); border-radius: 14px; padding: 20px; margin-left: -20px; margin-right: -20px; backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); }

/* Duo */
.duo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 32px; }
.duo-card { border-radius: 12px; padding: 16px 18px; display: flex; align-items: flex-start; gap: 12px; position: relative; overflow: hidden; }
.duo-accent { position: absolute; left: 0; top: 0; bottom: 0; width: 3px; }
.accent-green { background: #34d399; }
.accent-red { background: #f87171; }
.duo-green { background: linear-gradient(135deg, rgba(52,211,153,0.1) 0%, rgba(12,12,14,0.75) 50%); border: 1px solid rgba(52,211,153,0.15); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
.duo-red { background: linear-gradient(135deg, rgba(248,113,113,0.08) 0%, rgba(12,12,14,0.75) 50%); border: 1px solid rgba(248,113,113,0.12); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
.duo-icon { width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; background: rgba(52,211,153,0.15); color: #34d399; }
.duo-icon-red { background: rgba(248,113,113,0.15); color: #f87171; }
.duo-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px; }
.duo-green .duo-label { color: #34d399; } .duo-red .duo-label { color: #f87171; }
.duo-text { font-size: 13px; line-height: 1.6; color: var(--text); }

/* Performance */
.perf-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.perf-toggle { display: flex; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.perf-toggle button {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 32px; border: none; cursor: pointer;
  background: transparent; color: var(--text-muted);
  transition: all 0.15s; font-family: inherit;
}
.perf-toggle button:first-child { border-right: 1px solid var(--border); }
.perf-toggle button.active { background: var(--bg-elevated); color: var(--text-heading); }
.perf-toggle button:hover:not(.active) { color: var(--text-strong); }

/* View A: Radar + rings */
.perf-card {
  display: flex; align-items: center; gap: 8px;
  background: rgba(12,12,14,0.7); border: 1px solid var(--border);
  border-radius: 16px; padding: 16px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.perf-radar { flex-shrink: 0; }
.perf-rings { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
.ring-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; transition: background 0.15s; }
.ring-item:hover { background: rgba(255,255,255,0.03); }
.ring-wrap { position: relative; width: 56px; height: 56px; flex-shrink: 0; border-radius: 50%; }
.ring-bg {
  position: absolute; inset: 0; border-radius: 50%;
  background: rgba(255,255,255,0.05);
  mask: radial-gradient(circle, transparent 60%, #000 61%, #000 100%);
  -webkit-mask: radial-gradient(circle, transparent 60%, #000 61%, #000 100%);
}
.ring-fill {
  position: absolute; inset: 0; border-radius: 50%;
  mask: radial-gradient(circle, transparent 60%, #000 61%, #000 100%);
  -webkit-mask: radial-gradient(circle, transparent 60%, #000 61%, #000 100%);
  transition: background 0.6s var(--ease-spring);
}
.ring-score {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums;
}
.ring-name { font-size: 11px; font-weight: 500; color: var(--text-muted); line-height: 1.3; }

/* View B: Horizontal bars */
.perf-bars-card {
  background: rgba(12,12,14,0.7); border: 1px solid var(--border);
  border-radius: 16px; padding: 20px 24px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  display: flex; flex-direction: column; gap: 14px;
}
.bar-row { display: flex; flex-direction: column; gap: 6px; }
.bar-info { display: flex; align-items: baseline; justify-content: space-between; }
.bar-label { font-size: 12px; font-weight: 500; color: var(--text-muted); }
.bar-score { font-size: 18px; font-weight: 700; font-variant-numeric: tabular-nums; }
.bar-track { height: 6px; background: rgba(255,255,255,0.04); border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s var(--ease-spring); }

/* Did */
.did-list { display: flex; flex-direction: column; gap: 4px; }
.did-item { display: flex; align-items: flex-start; gap: 10px; padding: 6px 0; }
.did-num { width: 22px; height: 22px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 600; color: var(--text-muted); background: var(--bg-elevated); flex-shrink: 0; margin-top: 1px; }
.did-text { font-size: 13px; line-height: 1.5; color: var(--text); }

/* Narrative What I Did */
.narrative-list { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.narrative-item { display: flex; align-items: flex-start; gap: 12px; }
.narrative-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 8px; }
.narrative-text { font-size: 14px; line-height: 1.7; color: var(--text-strong); }

/* Continued + Roadblocks */
.cont-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 32px; }
.cont-card { padding: 18px 20px; border-radius: 12px; background: rgba(12,12,14,0.7); border: 1px solid var(--border); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
.cont-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.cont-list li { display: flex; align-items: flex-start; gap: 10px; font-size: 13px; line-height: 1.6; color: var(--text); }
.cont-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text-muted); flex-shrink: 0; margin-top: 7px; }
.dot-amber { background: var(--amber); }

/* Insights */
.insights-list { list-style: none; display: flex; flex-direction: column; gap: 14px; }
.insight-item { display: flex; align-items: flex-start; gap: 14px; }
.insight-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; margin-top: 8px; }
.insight-text { font-size: 14px; line-height: 1.7; color: var(--text-strong); }

/* Activity Timeline toggle */
.timeline-toggle {
  display: flex; align-items: center; gap: 8px; width: 100%;
  padding: 12px 16px; border-radius: 10px;
  background: rgba(12,12,14,0.7); border: 1px solid var(--border);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  color: var(--text-muted); font-size: 13px; font-weight: 500;
  font-family: inherit; cursor: pointer; transition: all 0.2s;
}
.timeline-toggle:hover { border-color: var(--border-hover); color: var(--text-strong); }
.toggle-chevron { transition: transform 0.3s var(--ease-spring); flex-shrink: 0; }
.toggle-chevron.open { transform: rotate(90deg); }
.toggle-count { margin-left: auto; font-size: 11px; color: var(--text-muted); }

.timeline-list { padding: 12px 0 0; display: flex; flex-direction: column; gap: 2px; }
.tl-item { display: flex; align-items: flex-start; gap: 10px; padding: 6px 16px; }
.tl-num { width: 22px; height: 22px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 600; color: var(--text-muted); background: var(--bg-elevated); flex-shrink: 0; margin-top: 1px; }
.tl-text { font-size: 13px; line-height: 1.5; color: var(--text); }

/* Expand transition */
.expand-enter-active, .expand-leave-active { transition: all 0.3s var(--ease-spring); overflow: hidden; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; }
.expand-enter-to, .expand-leave-from { opacity: 1; max-height: 1200px; }

/* Themes */
.theme-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px; }
.theme-card { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 10px; background: rgba(12,12,14,0.7); border: 1px solid var(--border); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); transition: all 0.15s; }
.theme-card:hover { border-color: var(--border-hover); }
.theme-icon { font-size: 16px; opacity: 0.5; }
.theme-body { display: flex; flex-direction: column; }
.theme-name { font-size: 12px; font-weight: 500; color: var(--text-strong); }
.theme-count { font-size: 10px; color: var(--text-muted); }

/* Volume */
.vol-card { background: rgba(12,12,14,0.7); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
.vol-bar { display: flex; height: 6px; border-radius: 3px; overflow: hidden; gap: 2px; margin-bottom: 10px; }
.vol-add-bar { background: #34d399; border-radius: 3px; } .vol-del-bar { background: #f87171; border-radius: 3px; }
.vol-labels { display: flex; gap: 16px; }
.vol-add { font-size: 12px; font-weight: 600; color: #34d399; } .vol-del { font-size: 12px; font-weight: 600; color: #f87171; } .vol-files { font-size: 12px; color: var(--text-muted); margin-left: auto; }

/* Projects */
.project-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.project-tag { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; font-size: 12px; color: var(--text); background: rgba(12,12,14,0.7); border: 1px solid var(--border); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }

/* Docs */
.docs-list { display: flex; flex-direction: column; gap: 4px; }
.doc-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; }
.doc-title { font-size: 13px; font-weight: 500; color: var(--text-strong); }
.doc-leader { flex: 1; height: 1px; background: var(--border); min-width: 12px; }
.doc-desc { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }

/* Hours */
.hours-card { background: rgba(12,12,14,0.7); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
.hour-row { display: flex; align-items: center; gap: 8px; }
.hour-label { font-size: 11px; font-variant-numeric: tabular-nums; color: var(--text-muted); width: 40px; text-align: right; }
.hour-track { flex: 1; height: 6px; background: var(--bg-elevated); border-radius: 3px; overflow: hidden; }
.hour-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.hour-n { font-size: 11px; color: var(--text-muted); width: 24px; font-variant-numeric: tabular-nums; }

/* Commands */
.cmd-card { background: rgba(12,12,14,0.7); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
.cmd-row { display: flex; align-items: center; gap: 10px; padding: 3px 0; }
.cmd-time { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.cmd-text { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Git */
.git-card { background: rgba(12,12,14,0.7); border: 1px solid var(--border); border-radius: 12px; margin-bottom: 10px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); display: flex; overflow: hidden; }
.git-accent { width: 3px; background: var(--green); flex-shrink: 0; }
.git-inner { flex: 1; padding: 16px 18px; }
.repo-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.repo-name { font-size: 14px; font-weight: 600; color: var(--text-strong); } .repo-stat { font-size: 11px; color: var(--text-muted); margin-left: auto; }
.commits { display: flex; flex-direction: column; gap: 4px; }
.commit { display: flex; align-items: baseline; gap: 8px; padding: 3px 0; }
.chash { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--purple); background: var(--purple-bg); padding: 2px 6px; border-radius: 4px; flex-shrink: 0; }
.ctime { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.cleader { flex: 1; height: 1px; background: var(--border); min-width: 8px; }
.cmsg { font-size: 12px; color: var(--text); max-width: 450px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Files */
.files-card { background: rgba(12,12,14,0.7); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
.fgroup { margin-bottom: 10px; } .fgroup:last-child { margin-bottom: 0; }
.fdir { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: var(--text-strong); margin-bottom: 4px; }
.fcount { font-weight: 400; color: var(--text-muted); }
.fpath { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--text-muted); padding-left: 18px; line-height: 1.8; }

/* Reflection */
.reflect-card {
  background: rgba(12,12,14,0.7); border: 1px solid var(--border);
  border-radius: 16px; padding: 24px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}

/* Evaluation */
.reflect-eval { margin-bottom: 20px; padding-bottom: 18px; border-bottom: 1px solid var(--border); }
.eval-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.eval-tag { font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 6px; border: 1px solid; }
.eval-insights { list-style: none; display: flex; flex-direction: column; gap: 6px; }
.eval-insights li { font-size: 13px; line-height: 1.6; color: var(--text); padding-left: 14px; position: relative; }
.eval-insights li::before { content: '→'; position: absolute; left: 0; color: var(--text-muted); }

/* Scores layout: 3 left, average right */
.reflect-scores { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.rscores-left { display: flex; gap: 20px; }
.rscore { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.rscore-ring { position: relative; width: 48px; height: 48px; }
.rscore-ring svg { display: block; }
.rscore-num {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; font-variant-numeric: tabular-nums;
}
.rscore-label { font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); }
.rscore-avg { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.rscore-ring-lg { width: 72px; height: 72px; }
.rscore-num-lg { font-size: 20px; }

.reflect-text { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding-top: 18px; border-top: 1px solid var(--border); }
.rtext-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.rtext-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #34d399; }
.rtext-themes { display: flex; gap: 4px; }
.rtext-theme { font-size: 10px; color: var(--text-muted); background: rgba(255,255,255,0.04); padding: 2px 8px; border-radius: 4px; }
.rtext-content { font-size: 13px; line-height: 1.6; color: var(--text); }

/* Footer */
.footer { border-top: 1px solid var(--border); padding: 12px; text-align: center; }
.footer-text { font-size: 10px; font-variant-numeric: tabular-nums; color: var(--text-muted); }

@media (max-width: 640px) {
  .hero-h1 { font-size: 24px; }
  .hero-title-row { flex-direction: column; align-items: flex-start; gap: 12px; }
  .duo-grid { grid-template-columns: 1fr; }
  .perf-card { flex-direction: column; }
  .perf-rings { grid-template-columns: 1fr 1fr; }
  .theme-grid { grid-template-columns: 1fr; }
}
</style>
