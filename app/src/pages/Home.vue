<script setup>
import { ref, onMounted } from 'vue'

const manifest = ref({ work: [], daily: [] })
onMounted(async () => {
  manifest.value = await (await fetch('/manifest.json')).json()
})
</script>

<template>
  <div class="page">
    <div class="mx content">

      <!-- Journal Cards -->
      <div class="cards">
        <router-link to="/work" class="card">
          <div class="card-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
          </div>
          <div class="card-top">
            <h2 class="card-label">Work Journal</h2>
            <span class="badge">{{ manifest.work.length }}</span>
          </div>
          <p class="card-desc">Claude Code sessions, git commits, project work across all repos.</p>
          <div class="card-stats" v-if="manifest.work.length">
            <div class="card-stat">
              <span class="card-stat-val">{{ manifest.work.reduce((s, e) => s + (e.stats?.sessions || 0), 0) }}</span>
              <span class="card-stat-label">Total Sessions</span>
            </div>
            <div class="card-stat">
              <span class="card-stat-val">{{ manifest.work.reduce((s, e) => s + (e.stats?.commits || 0), 0) }}</span>
              <span class="card-stat-label">Total Commits</span>
            </div>
          </div>
        </router-link>

        <router-link to="/daily" class="card">
          <div class="card-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          </div>
          <div class="card-top">
            <h2 class="card-label">Daily Journal</h2>
            <span class="badge">{{ manifest.daily.length }}</span>
          </div>
          <p class="card-desc">Terminal activity, file changes, git commits, and development work.</p>
          <div class="card-stats" v-if="manifest.daily.length">
            <div class="card-stat">
              <span class="card-stat-val">{{ manifest.daily.reduce((s, e) => s + (e.stats?.commands || 0), 0) }}</span>
              <span class="card-stat-label">Total Commands</span>
            </div>
            <div class="card-stat">
              <span class="card-stat-val">{{ manifest.daily.reduce((s, e) => s + (e.stats?.commits || 0), 0) }}</span>
              <span class="card-stat-label">Total Commits</span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Recent Activity -->
      <section class="recent-section">
        <p class="section-label">Recent Activity</p>
        <div class="recent-list">
          <router-link
            v-for="entry in [...manifest.work.slice(0, 7)]"
            :key="'w-' + entry.date"
            :to="`/work/${entry.date}`"
            class="recent-row"
          >
            <span class="recent-type type-work">Work</span>
            <span class="recent-date">{{ entry.date }}</span>
            <span class="recent-day">{{ entry.day?.slice(0, 3) }}</span>
            <span class="recent-summary">{{ entry.summary }}</span>
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
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
  padding: 24px; transition: border-color 0.2s; display: block;
}
.card:hover { border-color: var(--border-hover); }
.card-icon { color: var(--text-muted); margin-bottom: 16px; }
.card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.card-label { font-size: 16px; font-weight: 700; color: var(--text-heading); letter-spacing: -0.01em; }
.badge { font-size: 11px; font-weight: 600; color: var(--text-muted); background: var(--bg-elevated); padding: 3px 10px; border-radius: 6px; }
.card-desc { font-size: 13px; color: var(--text-muted); line-height: 1.5; margin-bottom: 20px; }
.card-stats { display: flex; gap: 24px; padding-top: 16px; border-top: 1px solid var(--border); }
.card-stat { display: flex; flex-direction: column; gap: 2px; }
.card-stat-val { font-size: 18px; font-weight: 700; color: var(--text-heading); font-variant-numeric: tabular-nums; }
.card-stat-label { font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); }

/* Recent */
.recent-section { }
.section-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 12px; }
.recent-list { display: flex; flex-direction: column; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.recent-row {
  display: grid; grid-template-columns: 48px 90px 36px 1fr;
  gap: 10px; align-items: center;
  padding: 10px 16px; border-bottom: 1px solid var(--border);
  font-size: 13px; transition: background 0.1s;
}
.recent-row:last-child { border-bottom: none; }
.recent-row:hover { background: var(--bg-elevated); }
.recent-type { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; border-radius: 4px; padding: 2px 6px; text-align: center; }
.type-work { color: var(--blue); background: var(--blue-bg); }
.type-daily { color: var(--green); background: var(--green-bg); }
.recent-date { font-weight: 500; color: var(--text-strong); font-variant-numeric: tabular-nums; }
.recent-day { color: var(--text-muted); font-size: 12px; }
.recent-summary { color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 640px) {
  .cards { grid-template-columns: 1fr; }
  .recent-row { grid-template-columns: 48px 90px 1fr; }
  .recent-day { display: none; }
}
</style>
