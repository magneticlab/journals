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
const title = computed(() => isWork.value ? 'Work Journal' : 'Daily Journal')

const catIcons = {
  'Git': 'M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65S8.93 17.38 9 18v4',
  'Claude Code': 'M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z',
  'Navigation': 'M3 12h18M3 6h18M3 18h18',
  'File Inspection': 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z',
  'Package Management': 'M16.5 9.4l-9-5.19M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z',
  'Homebrew': 'M17 8h1a4 4 0 1 1 0 8h-1M3 8h1a4 4 0 0 1 0 8H3zM5 8v8M19 8v8',
  'Remote': 'M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z',
  'GitHub CLI': 'M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65S8.93 17.38 9 18v4',
  'File Operations': 'M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z',
  'Docker': 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z',
  'Python': 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z',
  'HTTP': 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z',
  'Other': 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z',
  'Design System': 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5',
  'Design & Layout': 'M5 3a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2H5z',
  'Page Building': 'M3 9h18M9 21V9',
  'Animation & Effects': 'M13 2L3 14h9l-1 8 10-12h-9l1-8z',
  'Bug Fixes': 'M8 2l1.88 1.88M14.12 3.88L16 2M9 7.13v-1a3.003 3.003 0 1 1 6 0v1',
  'Git & Deployment': 'M6 3v12M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  'Version Iteration': 'M21 12a9 9 0 1 1-6.219-8.56',
  'Refactoring': 'M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8',
  'Content & Copy': 'M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z',
  'Planning & Strategy': 'M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z',
  'General Development': 'M16 18l6-6-6-6M8 6l-6 6 6 6',
}
const genTime = computed(() => {
  if (!data.value?.generatedAt) return ''
  return new Date(data.value.generatedAt).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
})
</script>

<template>
  <div class="page">
    <!-- Sub-header -->
    <div class="header">
      <div class="mx header-inner">
        <div class="header-left">
          <router-link :to="`/${journal}`" class="back-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </router-link>
          <div>
            <p class="label">{{ title }}</p>
            <h1 class="htitle">{{ data?.day }}, {{ data?.display || date }}</h1>
          </div>
        </div>
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
    </div>

    <div v-if="loading" class="empty">Loading...</div>
    <div v-else-if="!data" class="empty">No entry for this date.</div>

    <div v-else class="mx body">

      <!-- Source -->
      <div class="badge-row">
        <span :class="['source-badge', isWork ? 'badge-blue' : 'badge-neutral']">
          {{ isWork ? 'From Claude history + git logs' : 'From shell history + git + filesystem' }}
        </span>
      </div>

      <!-- Went Right / Could Be Better -->
      <div v-if="data.wentRight || data.couldBeBetter" class="duo-grid">
        <div v-if="data.wentRight" class="duo-card duo-green">
          <p class="duo-label">Went Right</p>
          <p class="duo-text">{{ data.wentRight }}</p>
        </div>
        <div v-if="data.couldBeBetter" class="duo-card duo-red">
          <p class="duo-label">Could Be Better</p>
          <p class="duo-text">{{ data.couldBeBetter }}</p>
        </div>
      </div>

      <!-- What I Did (work) -->
      <section v-if="isWork && data.whatIDid?.length" class="section">
        <p class="section-label">What I Did</p>
        <ul class="blist">
          <li v-for="(item, i) in data.whatIDid" :key="i"><span class="dot"></span><span>{{ item }}</span></li>
        </ul>
      </section>

      <!-- Themes (work) -->
      <section v-if="isWork && data.themes && Object.keys(data.themes).length" class="section">
        <p class="section-label">Focus Areas</p>
        <div class="tags">
          <span v-for="(count, theme) in data.themes" :key="theme" class="tag"><svg v-if="catIcons[theme]" class="tag-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path :d="catIcons[theme]"/></svg>{{ theme }} <span class="tag-n">{{ count }}</span></span>
        </div>
      </section>

      <!-- Categories (daily) -->
      <section v-if="!isWork && data.categories && Object.keys(data.categories).length" class="section">
        <p class="section-label">Terminal Activity</p>
        <div class="tags">
          <span v-for="(count, cat) in data.categories" :key="cat" class="tag"><svg v-if="catIcons[cat]" class="tag-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path :d="catIcons[cat]"/></svg>{{ cat }} <span class="tag-n">{{ count }}</span></span>
        </div>
      </section>

      <!-- Activity by Hour (daily) -->
      <section v-if="!isWork && data.activityByHour && Object.keys(data.activityByHour).length" class="section">
        <p class="section-label">Activity by Hour</p>
        <div class="hours">
          <div v-for="(count, hour) in data.activityByHour" :key="hour" class="hour-row">
            <span class="hour-label">{{ hour }}:00</span>
            <div class="hour-track"><div class="hour-fill" :style="{ width: Math.min(count / Math.max(...Object.values(data.activityByHour)) * 100, 100) + '%' }"></div></div>
            <span class="hour-n">{{ count }}</span>
          </div>
        </div>
      </section>

      <!-- Projects (work) -->
      <section v-if="isWork && data.projectsWip?.length" class="section">
        <p class="section-label">Projects</p>
        <div class="tags">
          <span v-for="(p, i) in data.projectsWip" :key="i" class="tag">{{ p }}</span>
        </div>
      </section>

      <!-- Docs Created (work) -->
      <section v-if="isWork && data.docsCreated?.length" class="section">
        <p class="section-label slabel-purple">Docs Created</p>
        <div class="docs-list">
          <div v-for="(doc, i) in data.docsCreated" :key="i" class="doc-row">
            <span class="doc-title">{{ doc.title }}</span>
            <span class="doc-leader"></span>
            <span class="doc-desc">{{ doc.description }}</span>
          </div>
        </div>
      </section>

      <!-- Notable Commands (daily) -->
      <section v-if="!isWork && data.notableCommands?.length" class="section">
        <p class="section-label slabel-blue">Notable Commands</p>
        <div class="cmd-list">
          <div v-for="(cmd, i) in data.notableCommands.slice(0, 20)" :key="i" class="cmd-row">
            <span class="cmd-time">{{ cmd.time }}</span>
            <code class="cmd-text">{{ cmd.command }}</code>
          </div>
        </div>
      </section>

      <!-- Git Activity -->
      <section v-if="data.gitActivity?.length" class="section">
        <p class="section-label slabel-green">Git Activity</p>
        <div v-for="repo in data.gitActivity" :key="repo.repo" class="git-repo">
          <div class="repo-head">
            <span class="repo-name">{{ repo.repo }}</span>
            <span v-if="repo.stat" class="repo-stat">{{ repo.stat }}</span>
          </div>
          <div class="commits">
            <div v-for="c in repo.commits" :key="c.hash" class="commit">
              <code class="chash">{{ c.hash }}</code>
              <span class="ctime">{{ c.time }}</span>
              <span class="cleader"></span>
              <span class="cmsg">{{ c.message }}</span>
              <span class="cauthor">{{ c.author }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Files (daily) -->
      <section v-if="!isWork && data.fileGroups && Object.keys(data.fileGroups).length" class="section">
        <p class="section-label">Files Modified</p>
        <div v-for="(files, dir) in data.fileGroups" :key="dir" class="fgroup">
          <p class="fdir">{{ dir }}/ <span class="fcount">({{ files.length }})</span></p>
          <p v-for="f in files" :key="f" class="fpath">{{ f }}</p>
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

/* Header */
.header { border-bottom: 1px solid var(--border); background: var(--bg-card); padding: 20px 0; }
.mx { max-width: 880px; margin: 0 auto; padding-left: 24px; padding-right: 24px; }
.header-inner { display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 12px; }
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--border);
  color: var(--text-muted); transition: all 0.15s; flex-shrink: 0;
}
.back-btn:hover { border-color: var(--border-hover); color: var(--text-strong); }
.label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em; color: var(--text-muted); }
.htitle { margin-top: 2px; font-family: var(--serif); font-size: 22px; font-weight: 400; color: var(--text-heading); }
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

/* Body */
.body { padding-top: 24px; padding-bottom: 64px; }
.empty { padding: 80px 24px; text-align: center; font-size: 14px; color: var(--text-muted); }

/* Badge */
.badge-row { margin-bottom: 24px; }
.source-badge { display: inline-block; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; padding: 4px 12px; border-radius: 100px; }
.badge-blue { background: var(--blue-bg); color: var(--blue); }
.badge-neutral { background: var(--bg-elevated); color: var(--text-muted); }

/* Duo cards (went right / could be better) */
.duo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 32px; }
.duo-card { border-radius: 12px; padding: 16px 20px; }
.duo-green { background: var(--green-bg); border: 1px solid rgba(34,197,94,0.12); }
.duo-red { background: var(--red-bg); border: 1px solid rgba(239,68,68,0.12); }
.duo-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 8px; }
.duo-green .duo-label { color: var(--green); }
.duo-red .duo-label { color: var(--red); }
.duo-text { font-size: 13px; line-height: 1.65; color: var(--text); }

/* Sections */
.section { margin-bottom: 32px; }
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 12px; }
.slabel-green { color: var(--green); }
.slabel-purple { color: var(--purple); }
.slabel-blue { color: var(--blue); }

/* Bullet list */
.blist { list-style: none; display: flex; flex-direction: column; gap: 6px; }
.blist li { display: flex; align-items: flex-start; gap: 10px; font-size: 13px; line-height: 1.5; color: var(--text); }
.dot { width: 5px; height: 5px; border-radius: 50%; background: var(--border-hover); margin-top: 7px; flex-shrink: 0; }

/* Tags */
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text); padding: 5px 12px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-card); }
.tag-icon { color: var(--text-muted); flex-shrink: 0; }
.tag-n { color: var(--text-muted); margin-left: 2px; }

/* Docs created */
.docs-list { display: flex; flex-direction: column; gap: 2px; }
.doc-row { display: flex; align-items: baseline; gap: 8px; padding: 4px 0; }
.doc-title { font-size: 13px; font-weight: 500; color: var(--text-strong); flex-shrink: 0; }
.doc-leader { flex: 1; height: 1px; background: var(--border); min-width: 12px; }
.doc-desc { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }

/* Git */
.git-repo { margin-bottom: 16px; }
.repo-head { display: flex; align-items: baseline; gap: 8px; margin-bottom: 8px; }
.repo-name { font-size: 13px; font-weight: 600; color: var(--text-strong); }
.repo-stat { font-size: 11px; color: var(--text-muted); font-style: italic; }
.commits { display: flex; flex-direction: column; gap: 2px; }
.commit { display: flex; align-items: baseline; gap: 8px; padding: 3px 0; }
.chash { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--purple); background: var(--purple-bg); padding: 1px 6px; border-radius: 4px; flex-shrink: 0; }
.ctime { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.cleader { flex: 1; height: 1px; background: var(--border); min-width: 8px; }
.cmsg { font-size: 12px; color: var(--text); flex-shrink: 0; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cauthor { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }

/* Hour chart */
.hours { display: flex; flex-direction: column; gap: 4px; }
.hour-row { display: flex; align-items: center; gap: 8px; }
.hour-label { font-size: 11px; font-variant-numeric: tabular-nums; color: var(--text-muted); width: 40px; text-align: right; }
.hour-track { flex: 1; height: 6px; background: var(--bg-elevated); border-radius: 3px; overflow: hidden; }
.hour-fill { height: 100%; background: var(--blue); border-radius: 3px; transition: width 0.3s; }
.hour-n { font-size: 11px; color: var(--text-muted); width: 24px; font-variant-numeric: tabular-nums; }

/* Commands */
.cmd-list { display: flex; flex-direction: column; gap: 2px; }
.cmd-row { display: flex; align-items: center; gap: 10px; padding: 3px 0; }
.cmd-time { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.cmd-text { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--text); background: var(--bg-elevated); padding: 2px 8px; border-radius: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 700px; }

/* Files */
.fgroup { margin-bottom: 12px; }
.fdir { font-size: 13px; font-weight: 600; color: var(--text-strong); margin-bottom: 4px; }
.fcount { font-weight: 400; color: var(--text-muted); }
.fpath { font-size: 11px; font-family: ui-monospace, 'SF Mono', Consolas, monospace; color: var(--text-muted); padding-left: 12px; line-height: 1.8; }

/* Footer */
.footer { border-top: 1px solid var(--border); padding: 12px; text-align: center; }
.footer-text { font-size: 10px; font-variant-numeric: tabular-nums; color: var(--text-muted); }

@media (max-width: 640px) {
  .header-inner { flex-direction: column; align-items: flex-start; gap: 12px; }
  .duo-grid { grid-template-columns: 1fr; }
  .commit { flex-wrap: wrap; }
  .cmsg { max-width: 100%; }
}
</style>
