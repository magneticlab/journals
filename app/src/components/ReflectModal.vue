<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['close', 'submit'])

const step = ref(0)
const answers = ref({
  energy: 7,
  focus: 7,
  mood: 7,
  win: '',
  improve: '',
})

const questions = [
  { key: 'energy', type: 'scale', label: 'Energy', question: 'How was your energy level today?', low: 'Drained', high: 'Fully charged' },
  { key: 'focus', type: 'scale', label: 'Focus', question: 'How focused were you today?', low: 'Scattered', high: 'Laser focused' },
  { key: 'mood', type: 'scale', label: 'Mood', question: 'How are you feeling overall?', low: 'Rough day', high: 'Great day' },
  { key: 'win', type: 'text', label: 'Win', question: 'What was your biggest win today?', placeholder: 'Something you accomplished, learned, or are proud of...' },
  { key: 'improve', type: 'text', label: 'Improve', question: 'What would you do differently?', placeholder: 'Something to adjust, a lesson learned, or a focus for tomorrow...' },
]

const current = computed(() => questions[step.value])
const isLast = computed(() => step.value === questions.length - 1)
const progress = computed(() => ((step.value + 1) / questions.length) * 100)

function next() {
  if (isLast.value) {
    submit()
  } else {
    step.value++
  }
}

function prev() {
  if (step.value > 0) step.value--
}

function submit() {
  const today = new Date().toISOString().slice(0, 10)
  const reflection = {
    date: today,
    timestamp: new Date().toISOString(),
    scores: {
      energy: answers.value.energy,
      focus: answers.value.focus,
      mood: answers.value.mood,
    },
    win: answers.value.win,
    improve: answers.value.improve,
    average: Math.round((answers.value.energy + answers.value.focus + answers.value.mood) / 3 * 10) / 10,
  }

  // Save to localStorage
  const stored = JSON.parse(localStorage.getItem('reflections') || '{}')
  stored[today] = reflection
  localStorage.setItem('reflections', JSON.stringify(stored))

  emit('submit', reflection)
  emit('close')
}

function scaleColor(val) {
  if (val >= 8) return '#34d399'
  if (val >= 6) return '#fbbf24'
  if (val >= 4) return '#fb923c'
  return '#f87171'
}
</script>

<template>
  <Teleport to="body">
    <div class="reflect-overlay" @click.self="$emit('close')">
      <div class="reflect-modal">
        <!-- Progress bar -->
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>

        <!-- Header -->
        <div class="modal-header">
          <span class="step-label">{{ step + 1 }} / {{ questions.length }}</span>
          <button class="close-btn" @click="$emit('close')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Question -->
        <div class="question-area">
          <h2 class="question-text">{{ current.question }}</h2>

          <!-- Scale input -->
          <div v-if="current.type === 'scale'" class="scale-input">
            <div class="scale-value" :style="{ color: scaleColor(answers[current.key]) }">
              {{ answers[current.key] }}
            </div>
            <input type="range" min="1" max="10" step="1"
              v-model.number="answers[current.key]"
              class="scale-slider"
              :style="{ '--fill': scaleColor(answers[current.key]) }"
            />
            <div class="scale-labels">
              <span>{{ current.low }}</span>
              <span>{{ current.high }}</span>
            </div>
          </div>

          <!-- Text input -->
          <div v-else class="text-input">
            <textarea v-model="answers[current.key]"
              :placeholder="current.placeholder"
              rows="3" class="text-area"
              @keydown.meta.enter="next"
            ></textarea>
          </div>
        </div>

        <!-- Navigation -->
        <div class="modal-nav">
          <button v-if="step > 0" class="nav-back" @click="prev">Back</button>
          <div v-else></div>
          <button class="nav-next" @click="next" :class="{ final: isLast }">
            {{ isLast ? 'Save Reflection' : 'Next' }}
            <svg v-if="!isLast" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.reflect-overlay {
  position: fixed; inset: 0; z-index: 10000;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}

.reflect-modal {
  width: 100%; max-width: 480px;
  background: #141416; border: 1px solid var(--border);
  border-radius: 20px; overflow: hidden;
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
}

.progress-track { height: 3px; background: rgba(255,255,255,0.05); }
.progress-fill { height: 100%; background: linear-gradient(90deg, #fb923c, #34d399); border-radius: 2px; transition: width 0.4s var(--ease-spring); }

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px 0;
}
.step-label { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; }
.close-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; border-radius: 6px; display: flex; }
.close-btn:hover { color: var(--text-strong); background: rgba(255,255,255,0.05); }

.question-area { padding: 24px 24px 20px; }
.question-text { font-family: var(--serif); font-size: 24px; font-weight: 400; color: var(--text-heading); margin-bottom: 28px; line-height: 1.3; }

/* Scale */
.scale-input { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.scale-value { font-size: 48px; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1; }

.scale-slider {
  width: 100%; height: 6px; -webkit-appearance: none; appearance: none;
  background: rgba(255,255,255,0.06); border-radius: 3px; outline: none;
}
.scale-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%;
  background: var(--fill, #fbbf24); cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.scale-slider::-moz-range-thumb {
  width: 22px; height: 22px; border-radius: 50%; border: none;
  background: var(--fill, #fbbf24); cursor: pointer;
}

.scale-labels { display: flex; justify-content: space-between; width: 100%; font-size: 11px; color: var(--text-muted); }

/* Text */
.text-input { }
.text-area {
  width: 100%; padding: 14px 16px; border-radius: 12px;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border);
  color: var(--text-strong); font-size: 14px; font-family: inherit;
  line-height: 1.6; resize: none; outline: none;
  transition: border-color 0.15s;
}
.text-area::placeholder { color: var(--text-muted); }
.text-area:focus { border-color: var(--border-hover); }

/* Nav */
.modal-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px 24px;
}
.nav-back {
  padding: 10px 18px; border-radius: 10px; border: 1px solid var(--border);
  background: none; color: var(--text-muted); font-size: 13px; font-weight: 500;
  font-family: inherit; cursor: pointer; transition: all 0.15s;
}
.nav-back:hover { border-color: var(--border-hover); color: var(--text-strong); }
.nav-next {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 20px; border-radius: 10px; border: none;
  background: rgba(255,255,255,0.08); color: var(--text-heading);
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s var(--ease-spring);
}
.nav-next:hover { background: rgba(255,255,255,0.12); }
.nav-next.final { background: rgba(52,211,153,0.2); color: #34d399; }
.nav-next.final:hover { background: rgba(52,211,153,0.3); }
</style>
