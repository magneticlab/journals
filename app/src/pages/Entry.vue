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
const genTime = computed(() => {
  if (!data.value?.generatedAt) return ''
  return new Date(data.value.generatedAt).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
})
</script>

<template>
  <div class="page">
    <!-- Header -->
    <div class="header">
      <div class="mx header-inner">
        <div>
          <p class="label">{{ title }}</p>
          <h1 class="htitle">{{ data?.day }}, {{ data?.display || date }}</h1>
        </div>
        <div class="nav-controls">
          <router-link :to="`/${journal}`" class="nav-link">All Entries</router-link>
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
          <span v-for="(count, theme) in data.themes" :key="theme" class="tag">{{ theme }} <span class="tag-n">{{ count }}</span></span>
        </div>
      </section>

      <!-- Categories (daily) -->
      <section v-if="!isWork && data.categories && Object.keys(data.categories).length" class="section">
        <p class="section-label">Terminal Activity</p>
        <div class="tags">
          <span v-for="(count, cat) in data.categories" :key="cat" class="tag">{{ cat }} <span class="tag-n">{{ count }}</span></span>
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
.page { min-height: 100vh; }

/* Header */
.header { border-bottom: 1px solid var(--border); background: var(--bg-card); padding: 28px 0 24px; }
.mx { max-width: 880px; margin: 0 auto; padding-left: 24px; padding-right: 24px; }
.header-inner { display: flex; align-items: center; justify-content: space-between; }
.label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em; color: var(--text-muted); }
.htitle { margin-top: 4px; font-size: 18px; font-weight: 700; letter-spacing: -0.02em; color: var(--text-heading); }
.nav-controls { display: flex; align-items: center; gap: 12px; }
.nav-link { font-size: 12px; color: var(--text-muted); padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border); transition: all 0.15s; }
.nav-link:hover { border-color: var(--border-hover); color: var(--text-strong); }
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
.tag { font-size: 12px; color: var(--text); padding: 4px 12px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-card); }
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
