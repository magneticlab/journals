<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useTheme } from '../composables/useTheme'

const { current, THEMES } = useTheme()
const open = ref(false)
const wrapper = ref(null)

function select(id) {
  current.value = id
  open.value = false
}

function onClickOutside(e) {
  if (wrapper.value && !wrapper.value.contains(e.target)) open.value = false
}
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
        <button
          v-for="t in THEMES" :key="t.id"
          :class="['theme-option', { active: current === t.id }]"
          @click="select(t.id)"
        >
          <span class="option-icon">{{ t.icon }}</span>
          <span class="option-label">{{ t.label }}</span>
          <svg v-if="current === t.id" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
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
  color: var(--text-muted); cursor: pointer;
  transition: all 0.2s;
}
.theme-btn:hover { border-color: var(--border-hover); color: var(--text-heading); }

.theme-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  width: 180px; padding: 8px;
  background: rgba(18,18,22,0.95);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border); border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.5);
  z-index: 9999;
}
.dropdown-label {
  font-size: 9px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--text-muted);
  padding: 6px 10px 4px;
}
.theme-option {
  display: flex; align-items: center; gap: 8px; width: 100%;
  padding: 8px 10px; border-radius: 8px; border: none;
  background: none; color: var(--text); font-size: 13px;
  font-family: inherit; cursor: pointer; transition: all 0.15s;
  text-align: left;
}
.theme-option:hover { background: rgba(255,255,255,0.05); color: var(--text-heading); }
.theme-option.active { color: var(--text-heading); }
.theme-option.active svg { color: #34d399; }
.option-icon { font-size: 15px; }
.option-label { flex: 1; }

.fade-enter-active, .fade-leave-active { transition: all 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
