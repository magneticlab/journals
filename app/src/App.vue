<template>
  <div class="layout">
    <nav class="topnav">
      <router-link to="/" class="logo">Journals</router-link>
      <div class="nav-links">
        <router-link to="/work" class="nav-link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
          Work
        </router-link>
        <router-link to="/daily" class="nav-link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
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
.nav-links { display: flex; gap: 2px; }
.nav-link {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 6px;
  font-size: 12px; font-weight: 500;
  color: var(--text-muted); transition: all 0.15s;
}
.nav-link:hover { color: var(--text-strong); background: var(--bg-elevated); }
.nav-link.router-link-active { color: var(--text-heading); background: var(--bg-elevated); }
</style>
