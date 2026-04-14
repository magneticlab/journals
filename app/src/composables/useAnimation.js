import { ref, watch } from 'vue'

const ANIMATIONS = [
  { id: 'ribbons', label: 'Ribbons', icon: '〰️' },
  { id: 'blob', label: 'Amoeba', icon: '🫧' },
]

const current = ref(localStorage.getItem('journal-animation') || 'ribbons')

watch(current, (val) => localStorage.setItem('journal-animation', val))

export function useAnimation() {
  return { current, ANIMATIONS }
}
