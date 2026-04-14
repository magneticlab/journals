<template>
  <div class="layout">
    <nav class="topnav">
      <router-link to="/" class="logo">Journals</router-link>
      <div class="nav-links">
        <router-link to="/work" class="nav-link">Work</router-link>
        <router-link to="/daily" class="nav-link">Daily</router-link>
      </div>
    </nav>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topnav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 56px;
  border-bottom: 1px solid #1c1c1f;
  background: #09090b;
  position: sticky;
  top: 0;
  z-index: 50;
}

.logo {
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: -0.02em;
  color: #fff;
}

.nav-links {
  display: flex;
  gap: 0.25rem;
}

.nav-link {
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #71717a;
  transition: all 0.15s;
}

.nav-link:hover {
  color: #e4e4e7;
  background: #18181b;
}

.nav-link.router-link-active {
  color: #fff;
  background: #27272a;
}

.main {
  flex: 1;
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}
</style>
