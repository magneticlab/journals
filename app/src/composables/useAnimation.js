import { ref, watch } from 'vue'

const ANIMATIONS = [
  { id: 'ribbons', label: 'Ribbons', icon: 'ribbons' },
  { id: 'blob', label: 'Amoeba', icon: 'blob' },
  { id: 'diagonal', label: 'Stripes', icon: 'stripes' },
]

const current = ref(localStorage.getItem('journal-animation') || 'ribbons')

watch(current, (val) => localStorage.setItem('journal-animation', val))

export function useAnimation() {
  return { current, ANIMATIONS }
}
