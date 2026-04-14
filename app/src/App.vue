<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const activeJournal = computed(() => {
  const p = route.path
  if (p.startsWith('/work')) return 'work'
  if (p.startsWith('/daily')) return 'daily'
  return null
})
</script>

<template>
  <div class="layout">
    <nav class="topnav">
      <router-link to="/" class="logo">Journals</router-link>
      <div class="nav-tabs">
        <router-link to="/work" :class="['nav-tab', { active: activeJournal === 'work' }]">
          <div class="tab-icon icon-work">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
          </div>
          Work
        </router-link>
        <router-link to="/daily" :class="['nav-tab', { active: activeJournal === 'daily' }]">
          <div class="tab-icon icon-daily">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          </div>
          Daily
        </router-link>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<style scoped>
.layout { min-height: 100vh; }
.topnav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; height: 52px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-card);
  position: sticky; top: 0; z-index: 50;
}
.logo {
  font-family: var(--serif); font-weight: 400; font-size: 16px;
  color: var(--text-heading);
}
.nav-tabs { display: flex; gap: 4px; height: 100%; align-items: stretch; }
.nav-tab {
  display: flex; align-items: center; gap: 7px;
  padding: 0 14px; position: relative;
  font-size: 13px; font-weight: 500;
  color: var(--text-muted); transition: color 0.15s;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.nav-tab:hover { color: var(--text-strong); }
.nav-tab.active { color: var(--text-heading); }

/* Branded bottom border on active */
.nav-tab.active:has(.icon-work) { border-bottom-color: #6395ff; }
.nav-tab.active:has(.icon-daily) { border-bottom-color: #34d399; }

/* Fallback for browsers without :has() */
.nav-tab.active { border-bottom-color: var(--text-muted); }

.tab-icon {
  display: flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; border-radius: 6px;
  transition: all 0.15s;
}
.icon-work { color: #6395ff; background: rgba(99,149,255,0.1); }
.icon-daily { color: #34d399; background: rgba(52,211,153,0.1); }
.nav-tab.active .icon-work { background: rgba(99,149,255,0.18); }
.nav-tab.active .icon-daily { background: rgba(52,211,153,0.18); }
</style>
