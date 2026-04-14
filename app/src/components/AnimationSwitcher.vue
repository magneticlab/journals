<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAnimation } from '../composables/useAnimation'

const { current, ANIMATIONS } = useAnimation()
const open = ref(false)
const wrapper = ref(null)

const icons = {
  ribbons: '<path d="M2 6c4-2 8 2 12 0s8-2 12 0"/><path d="M2 12c4-2 8 2 12 0s8-2 12 0"/><path d="M2 18c4-2 8 2 12 0s8-2 12 0"/>',
  blob: '<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16"/>',
  stripes: '<line x1="4" y1="20" x2="20" y2="4"/><line x1="8" y1="20" x2="24" y2="4"/><line x1="0" y1="20" x2="16" y2="4"/>',
}

function select(id) { current.value = id; open.value = false }
function onClickOutside(e) { if (wrapper.value && !wrapper.value.contains(e.target)) open.value = false }
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="anim-wrap" ref="wrapper">
    <button class="anim-btn" @click="open = !open" title="Switch animation">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3c-1.2 0-2.4.6-3 1.5A3.5 3.5 0 0 0 5 8c0 3 2 5.5 4 8 1 1.25 2 2.5 3 4 1-1.5 2-2.75 3-4 2-2.5 4-5 4-8a3.5 3.5 0 0 0-4-3.5C14.4 3.6 13.2 3 12 3z"/>
      </svg>
    </button>
    <Transition name="fade">
      <div v-if="open" class="anim-dropdown">
        <p class="dropdown-label">Animation</p>
        <button v-for="a in ANIMATIONS" :key="a.id" :class="['anim-option', { active: current === a.id }]" @click="select(a.id)">
          <svg class="option-svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" v-html="icons[a.icon]"></svg>
          <span class="option-label">{{ a.label }}</span>
          <svg v-if="current === a.id" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.anim-wrap { position: relative; }
.anim-btn {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 8px;
  border: 1px solid var(--border); background: rgba(12,12,14,0.7);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  color: var(--text-muted); cursor: pointer; transition: all 0.2s;
}
.anim-btn:hover { border-color: var(--border-hover); color: var(--text-heading); }

.anim-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  width: 180px; padding: 8px;
  background: rgba(18,18,22,0.95);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border); border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.5); z-index: 9999;
}
.dropdown-label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); padding: 6px 10px 4px; }
.anim-option {
  display: flex; align-items: center; gap: 8px; width: 100%;
  padding: 8px 10px; border-radius: 8px; border: none;
  background: none; color: var(--text); font-size: 13px;
  font-family: inherit; cursor: pointer; transition: all 0.15s; text-align: left;
}
.anim-option:hover { background: rgba(255,255,255,0.05); color: var(--text-heading); }
.anim-option.active { color: var(--text-heading); }
.anim-option.active svg { color: #34d399; }
.option-svg { flex-shrink: 0; color: var(--text-muted); }
.option-label { flex: 1; }

.fade-enter-active, .fade-leave-active { transition: all 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
