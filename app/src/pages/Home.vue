<script setup>
import { ref, onMounted } from 'vue'

const manifest = ref({ work: [], daily: [] })

onMounted(async () => {
  const res = await fetch('/manifest.json')
  manifest.value = await res.json()
})
</script>

<template>
  <div class="home">
    <div class="hero">
      <h1>Journals</h1>
      <p class="subtitle">Daily work reports from Claude Code sessions and laptop activity.</p>
    </div>

    <div class="cards">
      <router-link to="/work" class="card">
        <div class="card-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
          </svg>
        </div>
        <h2>Work Journal</h2>
        <p class="card-desc">Claude Code sessions, git activity, project work</p>
        <span class="card-count">{{ manifest.work.length }} entries</span>
      </router-link>

      <router-link to="/daily" class="card">
        <div class="card-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </div>
        <h2>Daily Journal</h2>
        <p class="card-desc">Terminal commands, file changes, development activity</p>
        <span class="card-count">{{ manifest.daily.length }} entries</span>
      </router-link>
    </div>

    <div v-if="manifest.work.length" class="recent">
      <h3>Recent Work</h3>
      <div class="recent-list">
        <router-link
          v-for="entry in manifest.work.slice(0, 5)"
          :key="entry.date"
          :to="`/work/${entry.date}`"
          class="recent-item"
        >
          <span class="recent-date">{{ entry.date }}</span>
          <span class="recent-day">{{ entry.day }}</span>
          <span class="recent-summary">{{ entry.summary.slice(0, 100) }}{{ entry.summary.length > 100 ? '...' : '' }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  padding-top: 1rem;
}

.hero {
  margin-bottom: 2.5rem;
}

.hero h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.03em;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #71717a;
  font-size: 0.9375rem;
}

.cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 3rem;
}

.card {
  background: #18181b;
  border: 1px solid #27272a;
  border-radius: 10px;
  padding: 1.5rem;
  transition: all 0.2s;
  display: block;
}

.card:hover {
  border-color: #3f3f46;
  background: #1c1c1f;
}

.card-icon {
  color: #71717a;
  margin-bottom: 1rem;
}

.card h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 0.375rem;
}

.card-desc {
  font-size: 0.8125rem;
  color: #71717a;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.card-count {
  font-size: 0.75rem;
  font-weight: 500;
  color: #a1a1aa;
  background: #27272a;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.recent h3 {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.recent-list {
  display: flex;
  flex-direction: column;
}

.recent-item {
  display: grid;
  grid-template-columns: 100px 90px 1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #1c1c1f;
  font-size: 0.8125rem;
  align-items: center;
  transition: background 0.15s;
}

.recent-item:hover {
  background: #18181b;
}

.recent-date {
  font-weight: 500;
  color: #e4e4e7;
  font-variant-numeric: tabular-nums;
}

.recent-day {
  color: #52525b;
}

.recent-summary {
  color: #71717a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 600px) {
  .cards {
    grid-template-columns: 1fr;
  }
  .recent-item {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }
}
</style>
