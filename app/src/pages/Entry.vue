<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ journal: String, date: String })
const router = useRouter()
const data = ref(null)
const manifest = ref({ work: [], daily: [] })
const loading = ref(true)

onMounted(async () => {
  manifest.value = await (await fetch('/manifest.json')).json()
  loadEntry()
})
watch(() => props.date, loadEntry)

async function loadEntry() {
  loading.value = true
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
function goTo(e) { router.push(`/${props.journal}/${e.target.value}`) }

const isWork = computed(() => props.journal === 'work')
const brand = computed(() => isWork.value ? '#6395ff' : '#34d399')
const brandBg = computed(() => isWork.value ? 'rgba(99,149,255,' : 'rgba(52,211,153,')

const themeIcons = {
  'Design System': '⬡', 'Design & Layout': '◫', 'Page Building': '▦',
  'Animation & Effects': '✦', 'Bug Fixes': '⚠', 'Git & Deployment': '⎇',
  'Version Iteration': '↻', 'Refactoring': '⟲', 'Content & Copy': '¶',
  'Planning & Strategy': '◈', 'General Development': '⌘',
  'Git': '⎇', 'Claude Code': '◉', 'Navigation': '≡', 'File Inspection': '◧',
  'Package Management': '⬢', 'Homebrew': '⚗', 'Remote': '⚡', 'GitHub CLI': '⎇',
  'File Operations': '◧', 'Other': '◆', 'Docker': '◎', 'Python': '◉', 'HTTP': '◎',
}

function scoreColor(score) {
  if (score >= 80) return '#34d399'
  if (score >= 60) return '#6395ff'
  if (score >= 40) return '#fbbf24'
  return '#f87171'
}

const genTime = computed(() => {
  if (!data.value?.generatedAt) return ''
  return new Date(data.value.generatedAt).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
})

// Active hours computed
const activeHours = computed(() => {
  const tr = data.value?.stats?.timeRange
  if (!tr) return null
  const parts = tr.split('–')
  if (parts.length !== 2) return null
  const [h1, m1] = parts[0].split(':').map(Number)
  const [h2, m2] = parts[1].split(':').map(Number)
  const mins = (h2 * 60 + m2) - (h1 * 60 + m1)
  if (mins <= 0) return null
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
})
</script>

<template>
  <div class="page">
    <!-- Hero header -->
    <div class="hero" :style="{ borderBottomColor: brand + '20' }">
      <div class="mx">
        <!-- Nav row -->
        <div class="nav-row">
          <router-link :to="`/${journal}`" class="back-link">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
            All entries
          </router-link>
          <div class="date-nav">
            <button @click="goToPrev" :disabled="!hasPrev" :class="['nav-btn', { disabled: !hasPrev }]">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <select :value="date" @change="goTo" class="date-select">
              <option v-for="d in dates" :key="d" :value="d">{{ d }}</option>
            </select>
            <button @click="goToNext" :disabled="!hasNext" :class="['nav-btn', { disabled: !hasNext }]">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>
        </div>

        <!-- Title block -->
        <div v-if="data" class="hero-content">
          <h1 class="hero-date">{{ data.day }}, {{ data.display }}</h1>
          <div class="hero-stats">
            <div class="hstat" v-if="isWork && data.stats?.sessions">
              <span class="hstat-val">{{ data.stats.sessions }}</span>
              <span class="hstat-lbl">sessions</span>
            </div>
            <div class="hstat" v-if="data.stats?.commits">
              <span class="hstat-val">{{ data.stats.commits }}</span>
              <span class="hstat-lbl">commits</span>
            </div>
            <div class="hstat" v-if="data.stats?.repos">
              <span class="hstat-val">{{ data.stats.repos }}</span>
              <span class="hstat-lbl">repos</span>
            </div>
            <div class="hstat" v-if="!isWork && data.stats?.commands">
              <span class="hstat-val">{{ data.stats.commands }}</span>
              <span class="hstat-lbl">commands</span>
            </div>
            <div class="hstat" v-if="isWork && data.stats?.linesAdded">
              <span class="hstat-val hstat-add">+{{ data.stats.linesAdded.toLocaleString() }}</span>
              <span class="hstat-lbl">lines added</span>
            </div>
            <div class="hstat" v-if="isWork && activeHours">
              <span class="hstat-val">{{ activeHours }}</span>
              <span class="hstat-lbl">active</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="empty">Loading...</div>
    <div v-else-if="!data" class="empty">No entry for this date.</div>

    <div v-else class="mx body">

      <!-- Went Right / Could Be Better -->
      <div v-if="data.wentRight || data.couldBeBetter" class="duo-grid">
        <div v-if="data.wentRight" class="duo-card duo-green">
          <div class="duo-icon">✓</div>
          <div>
            <p class="duo-label">Went Right</p>
            <p class="duo-text">{{ data.wentRight }}</p>
          </div>
        </div>
        <div v-if="data.couldBeBetter" class="duo-card duo-red">
          <div class="duo-icon duo-icon-red">!</div>
          <div>
            <p class="duo-label">Could Be Better</p>
            <p class="duo-text">{{ data.couldBeBetter }}</p>
          </div>
        </div>
      </div>

      <!-- Performance Metrics -->
      <section v-if="isWork && data.metrics" class="section">
        <p class="section-label" :style="{ color: brand }">Performance</p>
        <div class="metrics-grid">
          <div v-for="(m, key) in data.metrics" :key="key" class="metric-card">
            <div class="metric-top">
              <span class="metric-label">{{ m.label }}</span>
              <span class="metric-score" :style="{ color: scoreColor(m.score) }">{{ m.score }}</span>
            </div>
            <div class="metric-bar-bg">
              <div class="metric-bar" :style="{ width: m.score + '%', background: scoreColor(m.score) }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- What I Did -->
      <section v-if="isWork && data.whatIDid?.length" class="section">
        <p class="section-label">What I Did</p>
        <div class="did-list">
          <div v-for="(item, i) in data.whatIDid" :key="i" class="did-item">
            <span class="did-num">{{ i + 1 }}</span>
            <span class="did-text">{{ item }}</span>
          </div>
        </div>
      </section>

      <!-- Focus Areas / Terminal Activity — as cards -->
      <section v-if="(isWork && data.themes && Object.keys(data.themes).length) || (!isWork && data.categories && Object.keys(data.categories).length)" class="section">
        <p class="section-label" :style="{ color: brand }">{{ isWork ? 'Focus Areas' : 'Terminal Activity' }}</p>
        <div class="theme-grid">
          <div
            v-for="(count, name) in (isWork ? data.themes : data.categories)"
            :key="name"
            class="theme-card"
          >
            <span class="theme-icon">{{ themeIcons[name] || '◆' }}</span>
            <div class="theme-body">
              <span class="theme-name">{{ name }}</span>
              <span class="theme-count">{{ count }} interactions</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Activity by Hour -->
      <section v-if="!isWork && data.activityByHour && Object.keys(data.activityByHour).length" class="section">
        <p class="section-label" :style="{ color: brand }">Activity by Hour</p>
        <div class="hours-card">
          <div v-for="(count, hour) in data.activityByHour" :key="hour" class="hour-row">
            <span class="hour-label">{{ hour }}:00</span>
            <div class="hour-track">
              <div class="hour-fill" :style="{ width: Math.min(count / Math.max(...Object.values(data.activityByHour)) * 100, 100) + '%', background: brand }"></div>
            </div>
            <span class="hour-n">{{ count }}</span>
          </div>
        </div>
      </section>

      <!-- Volume bar (work) -->
      <section v-if="isWork && (data.stats?.linesAdded || data.stats?.linesRemoved)" class="section">
        <p class="section-label">Code Volume</p>
        <div class="vol-card">
          <div class="vol-bar">
            <div class="vol-add-bar" :style="{ flex: data.stats.linesAdded || 1 }"></div>
            <div class="vol-del-bar" :style="{ flex: data.stats.linesRemoved || 1 }"></div>
          </div>
          <div class="vol-labels">
            <span class="vol-add">+{{ (data.stats.linesAdded || 0).toLocaleString() }} insertions</span>
            <span class="vol-del">-{{ (data.stats.linesRemoved || 0).toLocaleString() }} deletions</span>
            <span class="vol-files">{{ data.stats.filesChanged || 0 }} files changed</span>
          </div>
        </div>
      </section>

      <!-- Projects -->
      <section v-if="isWork && data.projectsWip?.length" class="section">
        <p class="section-label">Projects</p>
        <div class="project-tags">
          <div v-for="(p, i) in data.projectsWip" :key="i" class="project-tag">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            {{ p }}
          </div>
        </div>
      </section>

      <!-- Docs Created -->
      <section v-if="isWork && data.docsCreated?.length" class="section">
        <p class="section-label" style="color: var(--purple)">Docs Created</p>
        <div class="docs-list">
          <div v-for="(doc, i) in data.docsCreated" :key="i" class="doc-row">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
            <span class="doc-title">{{ doc.title }}</span>
            <span class="doc-leader"></span>
            <span class="doc-desc">{{ doc.description }}</span>
          </div>
        </div>
      </section>

      <!-- Notable Commands -->
      <section v-if="!isWork && data.notableCommands?.length" class="section">
        <p class="section-label" :style="{ color: brand }">Notable Commands</p>
        <div class="cmd-card">
          <div v-for="(cmd, i) in data.notableCommands.slice(0, 20)" :key="i" class="cmd-row">
            <span class="cmd-time">{{ cmd.time }}</span>
            <code class="cmd-text">{{ cmd.command }}</code>
          </div>
        </div>
      </section>

      <!-- Git Activity -->
      <section v-if="data.gitActivity?.length" class="section">
        <p class="section-label" style="color: var(--green)">Git Activity</p>
        <div v-for="repo in data.gitActivity" :key="repo.repo" class="git-card">
          <div class="repo-head">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="1.5"><path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>
            <span class="repo-name">{{ repo.repo }}</span>
            <span v-if="repo.stat" class="repo-stat">{{ repo.stat }}</span>
          </div>
          <div class="commits">
            <div v-for="c in repo.commits" :key="c.hash" class="commit">
              <code class="chash">{{ c.hash }}</code>
              <span class="ctime">{{ c.time }}</span>
              <span class="cleader"></span>
              <span class="cmsg">{{ c.message }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Files -->
      <section v-if="!isWork && data.fileGroups && Object.keys(data.fileGroups).length" class="section">
        <p class="section-label">Files Modified</p>
        <div class="files-card">
          <div v-for="(files, dir) in data.fileGroups" :key="dir" class="fgroup">
            <p class="fdir">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              {{ dir }}/ <span class="fcount">({{ files.length }})</span>
            </p>
            <p v-for="f in files" :key="f" class="fpath">{{ f }}</p>
          </div>
        </div>
      </section>

    </div>

    <!-- Footer -->
    <div v-if="data?.generatedAt" class="footer">
      <p class="footer-text">Generated {{ genTime }}</p>
    </div>
  </div>
</template>

<style scoped>
.page { min-height: calc(100vh - 52px); }

/* Hero header */
.hero {
  background: var(--bg-card); padding: 20px 0 28px;
  border-bottom: 2px solid;
}
.mx { max-width: 880px; margin: 0 auto; padding-left: 24px; padding-right: 24px; }

.nav-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.back-link {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--text-muted);
  padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border);
  transition: all 0.15s;
}
.back-link:hover { border-color: var(--border-hover); color: var(--text-strong); }

.date-nav { display: flex; align-items: center; gap: 4px; }
.nav-btn { padding: 6px; border-radius: 8px; border: none; background: none; cursor: pointer; color: var(--text-muted); transition: all 0.15s; display: flex; }
.nav-btn:hover { background: var(--bg-elevated); color: var(--text-strong); }
.nav-btn.disabled { color: var(--border); cursor: not-allowed; }
.date-select {
  appearance: none; border: 1px solid var(--border); border-radius: 8px;
  padding: 6px 12px; font-size: 12px; font-weight: 500; font-variant-numeric: tabular-nums;
  color: var(--text); background: var(--bg-card); cursor: pointer; outline: none; font-family: inherit; text-align: center;
}
.date-select:hover { border-color: var(--border-hover); }

.hero-content {}
.hero-date { font-family: var(--serif); font-size: 32px; font-weight: 400; color: var(--text-heading); margin-bottom: 16px; }
.hero-stats { display: flex; gap: 20px; flex-wrap: wrap; }
.hstat { display: flex; align-items: baseline; gap: 5px; }
.hstat-val { font-size: 20px; font-weight: 700; color: var(--text-heading); font-variant-numeric: tabular-nums; }
.hstat-add { color: #34d399; }
.hstat-lbl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

/* Body */
.body { padding-top: 28px; padding-bottom: 64px; }
.empty { padding: 80px 24px; text-align: center; font-size: 14px; color: var(--text-muted); }

/* Duo cards */
.duo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 32px; }
.duo-card {
  border-radius: 12px; padding: 16px 18px;
  display: flex; align-items: flex-start; gap: 12px;
}
.duo-green { background: rgba(52,211,153,0.06); border: 1px solid rgba(52,211,153,0.12); }
.duo-red { background: rgba(248,113,113,0.05); border: 1px solid rgba(248,113,113,0.1); }
.duo-icon {
  width: 24px; height: 24px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; flex-shrink: 0;
  background: rgba(52,211,153,0.15); color: #34d399;
}
.duo-icon-red { background: rgba(248,113,113,0.15); color: #f87171; }
.duo-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px; }
.duo-green .duo-label { color: #34d399; }
.duo-red .duo-label { color: #f87171; }
.duo-text { font-size: 13px; line-height: 1.6; color: var(--text); }

/* Sections */
.section { margin-bottom: 32px; }
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 12px; }

/* Metrics */
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.metric-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px;
  padding: 14px 16px; transition: border-color 0.15s;
}
.metric-card:hover { border-color: var(--border-hover); }
.metric-top { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 8px; }
.metric-label { font-size: 11px; font-weight: 500; color: var(--text-muted); }
.metric-score { font-size: 20px; font-weight: 700; font-variant-numeric: tabular-nums; }
.metric-bar-bg { height: 4px; background: var(--bg-elevated); border-radius: 2px; overflow: hidden; }
.metric-bar { height: 100%; border-radius: 2px; transition: width 0.5s ease-out; }

/* What I Did — numbered */
.did-list { display: flex; flex-direction: column; gap: 4px; }
.did-item { display: flex; align-items: flex-start; gap: 10px; padding: 6px 0; }
.did-num {
  width: 22px; height: 22px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 600; color: var(--text-muted);
  background: var(--bg-elevated); flex-shrink: 0; margin-top: 1px;
}
.did-text { font-size: 13px; line-height: 1.5; color: var(--text); }

/* Theme cards grid */
.theme-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px; }
.theme-card {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 10px;
  background: var(--bg-card); border: 1px solid var(--border);
  transition: all 0.15s;
}
.theme-card:hover { border-color: var(--border-hover); box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.theme-icon { font-size: 16px; opacity: 0.5; }
.theme-body { display: flex; flex-direction: column; }
.theme-name { font-size: 12px; font-weight: 500; color: var(--text-strong); }
.theme-count { font-size: 10px; color: var(--text-muted); }

/* Volume */
.vol-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; }
.vol-bar { display: flex; height: 6px; border-radius: 3px; overflow: hidden; gap: 2px; margin-bottom: 10px; }
.vol-add-bar { background: #34d399; border-radius: 3px; }
.vol-del-bar { background: #f87171; border-radius: 3px; }
.vol-labels { display: flex; gap: 16px; }
.vol-add { font-size: 12px; font-weight: 600; color: #34d399; }
.vol-del { font-size: 12px; font-weight: 600; color: #f87171; }
.vol-files { font-size: 12px; color: var(--text-muted); margin-left: auto; }

/* Projects */
.project-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.project-tag {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 8px; font-size: 12px;
  color: var(--text); background: var(--bg-card);
  border: 1px solid var(--border);
}
.project-tag svg { color: var(--text-muted); }

/* Docs */
.docs-list { display: flex; flex-direction: column; gap: 4px; }
.doc-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; }
.doc-title { font-size: 13px; font-weight: 500; color: var(--text-strong); }
.doc-leader { flex: 1; height: 1px; background: var(--border); min-width: 12px; }
.doc-desc { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }

/* Hours */
.hours-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; }
.hours-card .hour-row { display: flex; align-items: center; gap: 8px; }
.hour-label { font-size: 11px; font-variant-numeric: tabular-nums; color: var(--text-muted); width: 40px; text-align: right; }
.hour-track { flex: 1; height: 6px; background: var(--bg-elevated); border-radius: 3px; overflow: hidden; }
.hour-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.hour-n { font-size: 11px; color: var(--text-muted); width: 24px; font-variant-numeric: tabular-nums; }

/* Commands */
.cmd-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
.cmd-row { display: flex; align-items: center; gap: 10px; padding: 3px 0; }
.cmd-time { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.cmd-text { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Git */
.git-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 16px 18px; margin-bottom: 10px;
}
.repo-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.repo-name { font-size: 14px; font-weight: 600; color: var(--text-strong); }
.repo-stat { font-size: 11px; color: var(--text-muted); margin-left: auto; }
.commits { display: flex; flex-direction: column; gap: 4px; }
.commit { display: flex; align-items: baseline; gap: 8px; padding: 3px 0; }
.chash { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--purple); background: var(--purple-bg); padding: 2px 6px; border-radius: 4px; flex-shrink: 0; }
.ctime { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.cleader { flex: 1; height: 1px; background: var(--border); min-width: 8px; }
.cmsg { font-size: 12px; color: var(--text); max-width: 450px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Files */
.files-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; }
.fgroup { margin-bottom: 10px; }
.fgroup:last-child { margin-bottom: 0; }
.fdir { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: var(--text-strong); margin-bottom: 4px; }
.fdir svg { color: var(--text-muted); }
.fcount { font-weight: 400; color: var(--text-muted); }
.fpath { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--text-muted); padding-left: 18px; line-height: 1.8; }

/* Footer */
.footer { border-top: 1px solid var(--border); padding: 12px; text-align: center; }
.footer-text { font-size: 10px; font-variant-numeric: tabular-nums; color: var(--text-muted); }

@media (max-width: 640px) {
  .hero-date { font-size: 24px; }
  .hero-stats { gap: 12px; }
  .duo-grid { grid-template-columns: 1fr; }
  .theme-grid { grid-template-columns: 1fr; }
  .commit { flex-wrap: wrap; }
  .cmsg { max-width: 100%; }
}
</style>
