<template>
  <div class="layout">
    <nav class="topnav">
      <router-link to="/" class="logo">Journals</router-link>
      <div class="nav-links">
        <router-link to="/work" class="nav-link">Work</router-link>
        <router-link to="/daily" class="nav-link">Daily</router-link>
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
  font-weight: 700; font-size: 14px; letter-spacing: -0.02em;
  color: var(--text-heading);
}
.nav-links { display: flex; gap: 2px; }
.nav-link {
  padding: 6px 12px; border-radius: 6px;
  font-size: 12px; font-weight: 500;
  color: var(--text-muted); transition: all 0.15s;
}
.nav-link:hover { color: var(--text-strong); background: var(--bg-elevated); }
.nav-link.router-link-active { color: var(--text-heading); background: var(--bg-elevated); }
</style>
