<script setup>
import { ref, onMounted, computed } from 'vue'

const manifest = ref({ work: [], daily: [] })
onMounted(async () => {
  manifest.value = await (await fetch('/manifest.json')).json()
})

// Consolidate into day cards
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

// Group by week (current week) then month
const grouped = computed(() => {
  const now = new Date()
  const groups = []
  let currentGroup = null

  for (const d of days.value) {
    const dt = new Date(d.date + 'T12:00:00')
    const diffDays = Math.floor((now - dt) / 86400000)
    let groupKey, groupLabel

    if (diffDays < 7) {
      groupKey = 'this-week'
      groupLabel = 'This Week'
    } else if (diffDays < 14) {
      groupKey = 'last-week'
      groupLabel = 'Last Week'
    } else {
      const m = d.date.slice(0, 7)
      const months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
      groupKey = m
      groupLabel = `${months[parseInt(m.slice(5))]} ${m.slice(0, 4)}`
    }

    if (!currentGroup || currentGroup.key !== groupKey) {
      currentGroup = { key: groupKey, label: groupLabel, items: [] }
      groups.push(currentGroup)
    }
    currentGroup.items.push(d)
  }
  return groups
})

// Day label: "Monday" for this week, "Monday 14" for older
function dayLabel(d, groupKey) {
  if (groupKey === 'this-week') return d.day
  return d.day
}
function dateNum(d) {
  return parseInt(d.date.slice(8))
}

// Quick summary per day
function daySummary(d) {
  const parts = []
  if (d.work) {
    const s = d.work.stats
    if (s?.sessions) parts.push(`${s.sessions} session${s.sessions > 1 ? 's' : ''}`)
    if (s?.commits) parts.push(`${s.commits} commit${s.commits > 1 ? 's' : ''}`)
  }
  if (d.daily) {
    const s = d.daily.stats
    if (s?.commands) parts.push(`${s.commands} commands`)
  }
  return parts.join(' · ')
}

// Mini sparklines
function spark7(list, key) {
  const slice = list.slice(0, 7).reverse()
  const vals = slice.map(e => e.stats?.[key] || 0)
  const max = Math.max(...vals, 1)
  return vals.map(v => Math.max((v / max) * 100, 4))
}
const workSpark = computed(() => spark7(manifest.value.work, 'commits'))
const dailySpark = computed(() => spark7(manifest.value.daily, 'commits'))
</script>

<template>
  <div class="page">
    <div class="mx content">

      <!-- Journal Cards -->
      <div class="cards">
        <router-link to="/work" class="card card-work">
          <div class="card-head">
            <div class="card-icon icon-work">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
            </div>
            <span class="card-count">{{ manifest.work.length }}</span>
          </div>
          <h2 class="card-label">Work Journal</h2>
          <p class="card-desc">Claude Code sessions, git commits, project work across all repos.</p>
          <div class="card-bottom">
            <div class="card-stats">
              <div class="cstat">
                <span class="cstat-val">{{ manifest.work.reduce((s, e) => s + (e.stats?.sessions || 0), 0) }}</span>
                <span class="cstat-label">Sessions</span>
              </div>
              <div class="cstat">
                <span class="cstat-val">{{ manifest.work.reduce((s, e) => s + (e.stats?.commits || 0), 0) }}</span>
                <span class="cstat-label">Commits</span>
              </div>
            </div>
            <div class="mini-spark">
              <span class="spark-hint">7d</span>
              <div class="spark-bars">
                <div v-for="(h, i) in workSpark" :key="i" class="spark-bar bar-work" :style="{ height: h + '%' }"></div>
              </div>
            </div>
          </div>
        </router-link>

        <router-link to="/daily" class="card card-daily">
          <div class="card-head">
            <div class="card-icon icon-daily">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <span class="card-count">{{ manifest.daily.length }}</span>
          </div>
          <h2 class="card-label">Daily Journal</h2>
          <p class="card-desc">Terminal activity, file changes, git commits, and development work.</p>
          <div class="card-bottom">
            <div class="card-stats">
              <div class="cstat">
                <span class="cstat-val">{{ manifest.daily.reduce((s, e) => s + (e.stats?.commands || 0), 0) }}</span>
                <span class="cstat-label">Commands</span>
              </div>
              <div class="cstat">
                <span class="cstat-val">{{ manifest.daily.reduce((s, e) => s + (e.stats?.commits || 0), 0) }}</span>
                <span class="cstat-label">Commits</span>
              </div>
            </div>
            <div class="mini-spark">
              <span class="spark-hint">7d</span>
              <div class="spark-bars">
                <div v-for="(h, i) in dailySpark" :key="i" class="spark-bar bar-daily" :style="{ height: h + '%' }"></div>
              </div>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Timeline -->
      <section class="recent-section">
        <p class="section-label">Recent Activity</p>

        <div class="timeline">
          <div v-for="group in grouped" :key="group.key" class="tl-group">
            <!-- Group header -->
            <div class="group-header">
              <div class="group-dot"></div>
              <span class="group-label">{{ group.label }}</span>
            </div>

            <!-- Day cards -->
            <div class="group-entries">
              <div v-for="d in group.items" :key="d.date" class="day-card">
                <div class="day-line"></div>

                <!-- Calendar sticker -->
                <div class="cal-sticker">
                  <span class="cal-day">{{ d.day?.slice(0, 3) }}</span>
                  <span class="cal-num">{{ dateNum(d) }}</span>
                </div>

                <!-- Card content -->
                <div class="day-content">
                  <div class="day-cols">
                    <!-- Work column -->
                    <router-link v-if="d.work" :to="`/work/${d.date}`" class="day-col col-work">
                      <div class="col-head">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                        <span class="col-label">Work</span>
                      </div>
                      <p class="col-summary">{{ d.work.summary }}</p>
                      <div class="col-meta" v-if="d.work.stats">
                        <span v-if="d.work.stats.sessions">{{ d.work.stats.sessions }}s</span>
                        <span v-if="d.work.stats.commits">{{ d.work.stats.commits }}c</span>
                        <span v-if="d.work.stats.repos">{{ d.work.stats.repos }}r</span>
                      </div>
                    </router-link>
                    <div v-else class="day-col col-empty">
                      <span class="empty-label">No work session</span>
                    </div>

                    <!-- Daily column -->
                    <router-link v-if="d.daily" :to="`/daily/${d.date}`" class="day-col col-daily">
                      <div class="col-head">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                        <span class="col-label">Daily</span>
                      </div>
                      <p class="col-summary">{{ d.daily.summary }}</p>
                      <div class="col-meta" v-if="d.daily.stats">
                        <span v-if="d.daily.stats.commands">{{ d.daily.stats.commands }} cmd</span>
                        <span v-if="d.daily.stats.commits">{{ d.daily.stats.commits }}c</span>
                      </div>
                    </router-link>
                    <div v-else class="day-col col-empty">
                      <span class="empty-label">No daily log</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.page { min-height: calc(100vh - 52px); }
.mx { max-width: 880px; margin: 0 auto; padding: 0 24px; }
.content { padding: 32px 0 64px; }

/* Cards */
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 40px; }
.card { border-radius: 14px; padding: 24px; transition: border-color 0.2s; display: block; }
.card-work { background: rgba(99,149,255,0.03); border: 1px solid rgba(99,149,255,0.15); }
.card-work:hover { border-color: rgba(99,149,255,0.3); }
.card-daily { background: rgba(52,211,153,0.03); border: 1px solid rgba(52,211,153,0.15); }
.card-daily:hover { border-color: rgba(52,211,153,0.3); }
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
.mini-spark { display: flex; align-items: flex-end; gap: 4px; }
.spark-hint { font-size: 9px; color: var(--text-muted); writing-mode: vertical-rl; transform: rotate(180deg); margin-bottom: 2px; }
.spark-bars { display: flex; align-items: flex-end; gap: 2px; height: 32px; }
.spark-bar { width: 4px; border-radius: 2px; min-height: 2px; transition: height 0.3s; }
.bar-work { background: rgba(99,149,255,0.5); }
.bar-daily { background: rgba(52,211,153,0.5); }

/* Timeline */
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 16px; }
.timeline { position: relative; }

/* Group header */
.tl-group { margin-bottom: 4px; }
.group-header {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0; position: sticky; top: 52px;
  background: var(--bg); z-index: 10;
}
.group-dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--border-hover); background: var(--bg); flex-shrink: 0; }
.group-label { font-family: var(--serif); font-size: 15px; color: var(--text-heading); }

/* Day card */
.group-entries { padding-left: 4px; }
.day-card { display: flex; align-items: flex-start; position: relative; margin-left: 1px; gap: 0; }
.day-line { position: absolute; left: 22px; top: 0; bottom: 0; width: 1px; background: var(--border); }

/* Calendar sticker */
.cal-sticker {
  width: 44px; flex-shrink: 0; margin-top: 10px; margin-right: 12px;
  display: flex; flex-direction: column; align-items: center;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  padding: 6px 4px; position: relative; z-index: 1;
  transition: border-color 0.15s;
}
.day-card:hover .cal-sticker { border-color: var(--border-hover); }
.cal-day { font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); }
.cal-num { font-size: 18px; font-weight: 700; color: var(--text-heading); font-variant-numeric: tabular-nums; line-height: 1.1; }

/* Card content */
.day-content {
  flex: 1; margin: 6px 0;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px;
  overflow: hidden; transition: border-color 0.15s;
}
.day-card:hover .day-content { border-color: var(--border-hover); }

.day-cols { display: grid; grid-template-columns: 1fr 1fr; }

.day-col {
  padding: 12px 14px; transition: background 0.1s;
  display: flex; flex-direction: column; gap: 6px;
}
.day-col:first-child { border-right: 1px solid var(--border); }
.day-col:hover { background: var(--bg-elevated); }

.col-head { display: flex; align-items: center; gap: 5px; }
.col-work .col-head { color: #6395ff; }
.col-daily .col-head { color: #34d399; }
.col-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.col-summary { font-size: 11px; color: var(--text-muted); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.col-meta { display: flex; gap: 8px; font-size: 10px; color: var(--text-muted); font-variant-numeric: tabular-nums; margin-top: auto; }

.col-empty { display: flex; align-items: center; justify-content: center; min-height: 60px; }
.empty-label { font-size: 11px; color: var(--border-hover); font-style: italic; }

@media (max-width: 640px) {
  .cards { grid-template-columns: 1fr; }
  .day-cols { grid-template-columns: 1fr; }
  .day-col:first-child { border-right: none; border-bottom: 1px solid var(--border); }
  .cal-sticker { width: 36px; }
  .cal-num { font-size: 15px; }
}
</style>
