import { ref, watch } from 'vue'

const THEMES = [
  { id: 'dark', label: 'Midnight', icon: '🌙' },
  { id: 'aurora', label: 'Aurora', icon: '🌌' },
]

const current = ref(localStorage.getItem('journal-theme') || 'dark')

watch(current, (val) => {
  localStorage.setItem('journal-theme', val)
  applyTheme(val)
})

function applyTheme(id) {
  document.documentElement.setAttribute('data-theme', id)
}

// Apply on load
if (typeof document !== 'undefined') {
  applyTheme(current.value)
}

export function useTheme() {
  return { current, THEMES, applyTheme }
}
