<script setup>
import { ref, onMounted } from 'vue'

const manifest = ref({ work: [], daily: [] })
onMounted(async () => {
  manifest.value = await (await fetch('/manifest.json')).json()
})
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="mx">
        <p class="label">Journals</p>
        <h1 class="title">Morning Briefs</h1>
      </div>
    </div>
    <div class="mx content">
      <div class="cards">
        <router-link to="/work" class="card">
          <div class="card-top">
            <p class="card-label">Work Journal</p>
            <span class="badge">{{ manifest.work.length }}</span>
          </div>
          <p class="card-desc">Claude sessions, git commits, project work</p>
          <div v-if="manifest.work.length" class="card-preview">
            <div v-for="e in manifest.work.slice(0, 4)" :key="e.date" class="preview-row">
              <span class="preview-date">{{ e.date }}</span>
              <span class="preview-sep"></span>
              <span class="preview-summary">{{ e.summary }}</span>
            </div>
          </div>
        </router-link>
        <router-link to="/daily" class="card">
          <div class="card-top">
            <p class="card-label">Daily Journal</p>
            <span class="badge">{{ manifest.daily.length }}</span>
          </div>
          <p class="card-desc">Terminal activity, file changes, development</p>
          <div v-if="manifest.daily.length" class="card-preview">
            <div v-for="e in manifest.daily.slice(0, 4)" :key="e.date" class="preview-row">
              <span class="preview-date">{{ e.date }}</span>
              <span class="preview-sep"></span>
              <span class="preview-summary">{{ e.summary }}</span>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; }
.header { border-bottom: 1px solid var(--border); background: var(--bg-card); padding: 28px 0 24px; }
.mx { max-width: 880px; margin: 0 auto; padding: 0 24px; }
.label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em; color: var(--text-muted); }
.title { margin-top: 4px; font-size: 18px; font-weight: 700; letter-spacing: -0.02em; color: var(--text-heading); }
.content { padding: 28px 0 64px; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 20px; transition: border-color 0.15s; display: block;
}
.card:hover { border-color: var(--border-hover); }
.card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.card-label { font-size: 14px; font-weight: 600; color: var(--text-heading); }
.badge { font-size: 11px; font-weight: 500; color: var(--text-muted); background: var(--bg-elevated); padding: 2px 8px; border-radius: 4px; }
.card-desc { font-size: 12px; color: var(--text-muted); margin-bottom: 16px; }
.card-preview { border-top: 1px solid var(--border); padding-top: 12px; display: flex; flex-direction: column; gap: 5px; }
.preview-row { display: flex; align-items: center; gap: 8px; font-size: 11px; }
.preview-date { font-weight: 500; color: var(--text); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.preview-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--border-hover); flex-shrink: 0; }
.preview-summary { color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
@media (max-width: 640px) { .cards { grid-template-columns: 1fr; } }
</style>
