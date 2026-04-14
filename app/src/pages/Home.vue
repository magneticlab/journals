<script setup>
import { ref, onMounted, computed } from 'vue'

const manifest = ref({ work: [], daily: [] })
onMounted(async () => {
  manifest.value = await (await fetch('/manifest.json')).json()
})

// Merge + sort recent for timeline
const recent = computed(() => {
  const all = [
    ...manifest.value.work.slice(0, 10).map(e => ({ ...e, type: 'work' })),
    ...manifest.value.daily.slice(0, 10).map(e => ({ ...e, type: 'daily' })),
  ]
  all.sort((a, b) => b.date.localeCompare(a.date))
  // Deduplicate by date — keep work if both exist
  const seen = new Map()
  for (const e of all) {
    const key = e.date + e.type
    if (!seen.has(key)) seen.set(key, e)
  }
  return [...seen.values()].slice(0, 12)
})

// Mini sparklines (last 7 days)
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
        <!-- WORK -->
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

        <!-- DAILY -->
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

      <!-- Recent Timeline -->
      <section class="recent-section">
        <p class="section-label">Recent Activity</p>
        <div class="timeline">
          <router-link
            v-for="entry in recent"
            :key="entry.type + entry.date"
            :to="`/${entry.type}/${entry.date}`"
            class="tl-row"
          >
            <div class="tl-line"></div>
            <div :class="['tl-dot', entry.type === 'work' ? 'dot-work' : 'dot-daily']"></div>
            <div class="tl-content">
              <div class="tl-top">
                <span class="tl-date">{{ entry.date }}</span>
                <span :class="['tl-badge', entry.type === 'work' ? 'badge-work' : 'badge-daily']">{{ entry.type === 'work' ? 'Work' : 'Daily' }}</span>
              </div>
              <p class="tl-summary">{{ entry.summary }}</p>
            </div>
          </router-link>
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
.card {
  border-radius: 14px; padding: 24px; transition: border-color 0.2s; display: block;
}
.card-work { background: rgba(59,130,246,0.04); border: 1px solid rgba(59,130,246,0.15); }
.card-work:hover { border-color: rgba(59,130,246,0.3); }
.card-daily { background: rgba(34,197,94,0.04); border: 1px solid rgba(34,197,94,0.15); }
.card-daily:hover { border-color: rgba(34,197,94,0.3); }

.card-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px; }
.card-icon { display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 10px; }
.icon-work { background: rgba(59,130,246,0.1); color: var(--blue); }
.icon-daily { background: rgba(34,197,94,0.1); color: var(--green); }
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
.bar-work { background: rgba(59,130,246,0.5); }
.bar-daily { background: rgba(34,197,94,0.5); }

/* Recent Timeline */
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 12px; }
.timeline { position: relative; padding-left: 4px; }
.tl-row {
  display: flex; align-items: stretch; position: relative;
  border-radius: 8px; transition: background 0.1s; margin-left: 1px;
}
.tl-row:hover { background: var(--bg-card); }
.tl-row:hover .tl-dot { transform: scale(1.3); }
.tl-line { position: absolute; left: 4px; top: 0; bottom: 0; width: 1px; background: var(--border); }
.tl-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; margin-top: 14px; margin-right: 14px; position: relative; z-index: 1; transition: all 0.15s; }
.dot-work { background: var(--blue); border: 2px solid rgba(59,130,246,0.3); }
.dot-daily { background: var(--green); border: 2px solid rgba(34,197,94,0.3); }
.tl-content { flex: 1; padding: 8px 12px 8px 0; }
.tl-top { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.tl-date { font-size: 13px; font-weight: 500; color: var(--text-strong); font-variant-numeric: tabular-nums; }
.tl-badge { font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; padding: 2px 7px; border-radius: 4px; }
.badge-work { color: var(--blue); background: var(--blue-bg); }
.badge-daily { color: var(--green); background: var(--green-bg); }
.tl-summary { font-size: 12px; color: var(--text-muted); line-height: 1.5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 640px) { .cards { grid-template-columns: 1fr; } }
</style>
