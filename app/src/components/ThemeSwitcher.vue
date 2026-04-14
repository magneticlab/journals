<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useTheme } from '../composables/useTheme'

const { mode, current, THEMES, getAutoTheme } = useTheme()
const open = ref(false)
const wrapper = ref(null)

const icons = {
  moon: '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
  sunrise: '<path d="M17 18a5 5 0 0 0-10 0"/><line x1="12" y1="9" x2="12" y2="2"/><line x1="4.22" y1="10.22" x2="5.64" y2="11.64"/><line x1="1" y1="18" x2="3" y2="18"/><line x1="21" y1="18" x2="23" y2="18"/><line x1="18.36" y1="11.64" x2="19.78" y2="10.22"/><line x1="23" y1="22" x2="1" y2="22"/><polyline points="8 6 12 2 16 6"/>',
  sun: '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>',
  sunset: '<path d="M17 18a5 5 0 0 0-10 0"/><line x1="12" y1="9" x2="12" y2="2"/><line x1="4.22" y1="10.22" x2="5.64" y2="11.64"/><line x1="1" y1="18" x2="3" y2="18"/><line x1="21" y1="18" x2="23" y2="18"/><line x1="18.36" y1="11.64" x2="19.78" y2="10.22"/><line x1="23" y1="22" x2="1" y2="22"/><polyline points="16 6 12 10 8 6"/>',
  sparkles: '<path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z"/><path d="M5 19l1 3 1-3 3-1-3-1-1-3-1 3-3 1z"/>',
  clock: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
}

function select(id) { mode.value = id; open.value = false }
function onClickOutside(e) { if (wrapper.value && !wrapper.value.contains(e.target)) open.value = false }
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="theme-wrap" ref="wrapper">
    <button class="theme-btn" @click="open = !open" title="Switch theme">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
      </svg>
    </button>
    <Transition name="fade">
      <div v-if="open" class="theme-dropdown">
        <p class="dropdown-label">Theme</p>

        <!-- Auto mode -->
        <button :class="['theme-option', { active: mode === 'auto' }]" @click="select('auto')">
          <svg class="option-svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" v-html="icons.clock"></svg>
          <span class="option-label">Auto <span class="auto-hint">({{ getAutoTheme() }})</span></span>
          <svg v-if="mode === 'auto'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
        </button>

        <div class="dropdown-divider"></div>

        <!-- Manual themes -->
        <button v-for="t in THEMES" :key="t.id" :class="['theme-option', { active: mode === t.id }]" @click="select(t.id)">
          <svg class="option-svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" v-html="icons[t.icon]"></svg>
          <span class="option-label">{{ t.label }}</span>
          <svg v-if="mode === t.id" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.theme-wrap { position: relative; }
.theme-btn {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 8px;
  border: 1px solid var(--border); background: rgba(12,12,14,0.7);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  color: var(--text-muted); cursor: pointer; transition: all 0.2s;
}
.theme-btn:hover { border-color: var(--border-hover); color: var(--text-heading); }

.theme-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  width: 200px; padding: 8px;
  background: rgba(18,18,22,0.95);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border); border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.5); z-index: 9999;
}
.dropdown-label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); padding: 6px 10px 4px; }
.dropdown-divider { height: 1px; background: var(--border); margin: 4px 8px; }

.theme-option {
  display: flex; align-items: center; gap: 8px; width: 100%;
  padding: 8px 10px; border-radius: 8px; border: none;
  background: none; color: var(--text); font-size: 13px;
  font-family: inherit; cursor: pointer; transition: all 0.15s; text-align: left;
}
.theme-option:hover { background: rgba(255,255,255,0.05); color: var(--text-heading); }
.theme-option.active { color: var(--text-heading); }
.theme-option.active svg { color: #34d399; }
.option-svg { flex-shrink: 0; color: var(--text-muted); }
.option-label { flex: 1; }
.auto-hint { font-size: 11px; color: var(--text-muted); }

.fade-enter-active, .fade-leave-active { transition: all 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
