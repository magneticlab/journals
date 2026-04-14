import { ref, watch, computed } from 'vue'

const THEMES = [
  { id: 'midnight', label: 'Midnight', icon: 'moon', hours: [22, 5] },
  { id: 'dawn', label: 'Dawn', icon: 'sunrise', hours: [5, 9] },
  { id: 'daylight', label: 'Daylight', icon: 'sun', hours: [9, 17] },
  { id: 'dusk', label: 'Dusk', icon: 'sunset', hours: [17, 22] },
  { id: 'aurora', label: 'Aurora', icon: 'sparkles', hours: null },
]

function getAutoTheme() {
  const h = new Date().getHours()
  if (h >= 22 || h < 5) return 'midnight'
  if (h >= 5 && h < 9) return 'dawn'
  if (h >= 9 && h < 17) return 'daylight'
  return 'dusk'
}

const stored = localStorage.getItem('journal-theme')
const mode = ref(stored || 'auto') // 'auto' or a theme id
const current = computed(() => mode.value === 'auto' ? getAutoTheme() : mode.value)

watch(current, (val) => applyTheme(val), { immediate: false })
watch(mode, (val) => {
  localStorage.setItem('journal-theme', val)
  applyTheme(current.value)
})

function applyTheme(id) {
  document.documentElement.setAttribute('data-theme', id)
}

if (typeof document !== 'undefined') {
  applyTheme(current.value)
}

export function useTheme() {
  return { current, mode, THEMES, applyTheme, getAutoTheme }
}
