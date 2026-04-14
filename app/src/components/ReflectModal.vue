<script setup>
import { ref, computed } from 'vue'
import { analyzeReflection } from '../services/claude'

const emit = defineEmits(['close', 'submit'])

// Phases: 'questions' → 'processing' → 'results'
const phase = ref('questions')
const step = ref(0)
const processingStep = ref(0)
const savedReflection = ref(null)

const answers = ref({
  energy: 7, focus: 7, mood: 7, win: '', improve: '',
})

const questions = [
  { key: 'energy', type: 'scale', label: 'Energy', question: 'How was your energy level today?', low: 'Drained', high: 'Fully charged' },
  { key: 'focus', type: 'scale', label: 'Focus', question: 'How focused were you today?', low: 'Scattered', high: 'Laser focused' },
  { key: 'mood', type: 'scale', label: 'Mood', question: 'How are you feeling overall?', low: 'Rough day', high: 'Great day' },
  { key: 'win', type: 'text', label: 'Win', question: 'What was your biggest win today?', placeholder: 'Something you accomplished, learned, or are proud of...' },
  { key: 'improve', type: 'text', label: 'Improve', question: 'What would you do differently?', placeholder: 'Something to adjust, a lesson learned, or a focus for tomorrow...' },
]

const processingSteps = [
  { label: 'Collecting responses', icon: '📋' },
  { label: 'Calculating scores', icon: '📊' },
  { label: 'Generating insights', icon: '💡' },
  { label: 'Building report', icon: '✨' },
]

const current = computed(() => questions[step.value])
const isLast = computed(() => step.value === questions.length - 1)
const progress = computed(() => ((step.value + 1) / questions.length) * 100)

function next() {
  if (isLast.value) {
    startProcessing()
  } else {
    step.value++
  }
}
function prev() { if (step.value > 0) step.value-- }

async function startProcessing() {
  phase.value = 'processing'
  processingStep.value = 0

  // Start AI analysis in parallel with the animation
  const aiPromise = analyzeReflection({
    scores: { energy: answers.value.energy, focus: answers.value.focus, mood: answers.value.mood },
    win: answers.value.win,
    improve: answers.value.improve,
  })

  // Animate through processing steps
  await new Promise(resolve => {
    const interval = setInterval(() => {
      processingStep.value++
      if (processingStep.value >= processingSteps.length) {
        clearInterval(interval)
        resolve()
      }
    }, 600)
  })

  // Wait for AI result (may already be done)
  const aiResult = await aiPromise

  saveAndShowResults(aiResult)
}

function saveAndShowResults(aiResult) {
  const today = new Date().toISOString().slice(0, 10)
  const reflection = {
    date: today,
    timestamp: new Date().toISOString(),
    scores: { energy: answers.value.energy, focus: answers.value.focus, mood: answers.value.mood },
    win: answers.value.win,
    improve: answers.value.improve,
    average: Math.round((answers.value.energy + answers.value.focus + answers.value.mood) / 3 * 10) / 10,
    ai: aiResult || null,
  }

  const stored = JSON.parse(localStorage.getItem('reflections') || '{}')
  stored[today] = reflection
  localStorage.setItem('reflections', JSON.stringify(stored))

  savedReflection.value = reflection
  emit('submit', reflection)
  phase.value = 'results'
}

function scaleColor(val) {
  if (val >= 8) return '#34d399'
  if (val >= 6) return '#fbbf24'
  if (val >= 4) return '#fb923c'
  return '#f87171'
}

function ringColor(val) {
  const stops = [[0,[248,113,113]],[4,[251,146,60]],[6,[251,191,36]],[10,[52,211,153]]]
  let lo = stops[0], hi = stops[stops.length-1]
  for (let i = 0; i < stops.length-1; i++) { if (val >= stops[i][0] && val <= stops[i+1][0]) { lo = stops[i]; hi = stops[i+1]; break } }
  const t = (val - lo[0]) / (hi[0] - lo[0] || 1)
  const r = Math.round(lo[1][0]+(hi[1][0]-lo[1][0])*t), g = Math.round(lo[1][1]+(hi[1][1]-lo[1][1])*t), b = Math.round(lo[1][2]+(hi[1][2]-lo[1][2])*t)
  return `rgb(${r},${g},${b})`
}
</script>

<template>
  <Teleport to="body">
    <div class="reflect-overlay" @click.self="phase === 'results' ? (emit('close')) : null">
      <div class="reflect-modal">

        <!-- === QUESTIONS PHASE === -->
        <template v-if="phase === 'questions'">
          <div class="progress-track"><div class="progress-fill" :style="{ width: progress + '%' }"></div></div>
          <div class="modal-header">
            <span class="step-label">{{ step + 1 }} / {{ questions.length }}</span>
            <button class="close-btn" @click="$emit('close')"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg></button>
          </div>
          <div class="question-area">
            <h2 class="question-text">{{ current.question }}</h2>
            <div v-if="current.type === 'scale'" class="scale-input">
              <div class="scale-value" :style="{ color: scaleColor(answers[current.key]) }">{{ answers[current.key] }}</div>
              <input type="range" min="1" max="10" step="1" v-model.number="answers[current.key]" class="scale-slider" :style="{ '--fill': scaleColor(answers[current.key]) }" />
              <div class="scale-labels"><span>{{ current.low }}</span><span>{{ current.high }}</span></div>
            </div>
            <div v-else class="text-input">
              <textarea v-model="answers[current.key]" :placeholder="current.placeholder" rows="3" class="text-area" @keydown.meta.enter="next"></textarea>
            </div>
          </div>
          <div class="modal-nav">
            <button v-if="step > 0" class="nav-back" @click="prev">Back</button><div v-else></div>
            <button class="nav-next" @click="next" :class="{ final: isLast }">{{ isLast ? 'Submit' : 'Next' }}<svg v-if="!isLast" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg></button>
          </div>
        </template>

        <!-- === PROCESSING PHASE === -->
        <template v-if="phase === 'processing'">
          <div class="processing">
            <div class="proc-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="proc-spinner"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </div>
            <h2 class="proc-title">Building your report</h2>
            <div class="proc-steps">
              <div v-for="(s, i) in processingSteps" :key="i" :class="['proc-step', { done: i < processingStep, active: i === processingStep }]">
                <span class="proc-check">
                  <svg v-if="i < processingStep" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                  <span v-else-if="i === processingStep" class="proc-dot"></span>
                  <span v-else class="proc-dot proc-dot-inactive"></span>
                </span>
                <span class="proc-step-label">{{ s.label }}</span>
              </div>
            </div>
          </div>
        </template>

        <!-- === RESULTS PHASE === -->
        <template v-if="phase === 'results' && savedReflection">
          <div class="results">
            <div class="results-header">
              <div class="results-badge">✓ Saved</div>
              <button class="close-btn" @click="$emit('close')"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg></button>
            </div>
            <h2 class="results-title">Your Daily Reflection</h2>

            <!-- Score rings -->
            <div class="results-scores">
              <div v-for="(val, key) in savedReflection.scores" :key="key" class="res-score">
                <div class="res-ring">
                  <svg width="56" height="56" viewBox="0 0 56 56">
                    <circle cx="28" cy="28" r="23" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="3.5" />
                    <circle cx="28" cy="28" r="23" fill="none" :stroke="ringColor(val)" stroke-width="3.5" stroke-linecap="round" :stroke-dasharray="`${val * 14.45} 200`" transform="rotate(-90 28 28)" />
                  </svg>
                  <span class="res-num" :style="{ color: ringColor(val) }">{{ val }}</span>
                </div>
                <span class="res-label">{{ key }}</span>
              </div>
              <div class="res-score res-avg">
                <div class="res-ring">
                  <svg width="56" height="56" viewBox="0 0 56 56">
                    <circle cx="28" cy="28" r="23" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="3.5" />
                    <circle cx="28" cy="28" r="23" fill="none" :stroke="ringColor(savedReflection.average)" stroke-width="3.5" stroke-linecap="round" :stroke-dasharray="`${savedReflection.average * 14.45} 200`" transform="rotate(-90 28 28)" />
                  </svg>
                  <span class="res-num" :style="{ color: ringColor(savedReflection.average) }">{{ savedReflection.average }}</span>
                </div>
                <span class="res-label">Average</span>
              </div>
            </div>

            <!-- AI Analysis -->
            <div v-if="savedReflection.ai" class="results-ai">
              <p class="ai-summary">{{ savedReflection.ai.summary }}</p>
              <div v-if="savedReflection.ai.tags?.length" class="ai-tags">
                <span v-for="t in savedReflection.ai.tags" :key="t" class="ai-tag">{{ t }}</span>
              </div>
            </div>

            <!-- Text responses with AI highlights -->
            <div class="results-text" v-if="savedReflection.win || savedReflection.improve">
              <div v-if="savedReflection.win" class="res-block">
                <p class="res-block-label">Biggest Win</p>
                <p class="res-block-text">{{ savedReflection.win }}</p>
                <div v-if="savedReflection.ai?.winHighlights?.length" class="res-highlights hl-g">
                  <ul><li v-for="h in savedReflection.ai.winHighlights" :key="h">{{ h }}</li></ul>
                </div>
              </div>
              <div v-if="savedReflection.improve" class="res-block">
                <p class="res-block-label" style="color: var(--amber)">What to Improve</p>
                <p class="res-block-text">{{ savedReflection.improve }}</p>
                <div v-if="savedReflection.ai?.improveHighlights?.length" class="res-highlights hl-a">
                  <ul><li v-for="h in savedReflection.ai.improveHighlights" :key="h">{{ h }}</li></ul>
                </div>
              </div>
            </div>

            <!-- AI Advice -->
            <div v-if="savedReflection.ai?.advice" class="ai-advice">
              <span class="advice-icon">💡</span>
              <p>{{ savedReflection.ai.advice }}</p>
            </div>

            <p class="results-hint">This reflection is saved to your daily journal report.</p>

            <button class="results-close" @click="$emit('close')">Done</button>
          </div>
        </template>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.reflect-overlay {
  position: fixed; inset: 0; z-index: 10000;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; padding: 24px;
}
.reflect-modal {
  width: 100%; max-width: 480px;
  background: #141416; border: 1px solid var(--border);
  border-radius: 20px; overflow: hidden;
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
}

/* Questions */
.progress-track { height: 3px; background: rgba(255,255,255,0.05); }
.progress-fill { height: 100%; background: linear-gradient(90deg, #fb923c, #34d399); border-radius: 2px; transition: width 0.4s var(--ease-spring); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px 0; }
.step-label { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; }
.close-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; border-radius: 6px; display: flex; }
.close-btn:hover { color: var(--text-strong); background: rgba(255,255,255,0.05); }
.question-area { padding: 24px 24px 20px; }
.question-text { font-family: var(--serif); font-size: 24px; font-weight: 400; color: var(--text-heading); margin-bottom: 28px; line-height: 1.3; }
.scale-input { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.scale-value { font-size: 48px; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1; }
.scale-slider { width: 100%; height: 6px; -webkit-appearance: none; appearance: none; background: rgba(255,255,255,0.06); border-radius: 3px; outline: none; }
.scale-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%; background: var(--fill, #fbbf24); cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.scale-slider::-moz-range-thumb { width: 22px; height: 22px; border-radius: 50%; border: none; background: var(--fill, #fbbf24); cursor: pointer; }
.scale-labels { display: flex; justify-content: space-between; width: 100%; font-size: 11px; color: var(--text-muted); }
.text-area { width: 100%; padding: 14px 16px; border-radius: 12px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); color: var(--text-strong); font-size: 14px; font-family: inherit; line-height: 1.6; resize: none; outline: none; transition: border-color 0.15s; }
.text-area::placeholder { color: var(--text-muted); }
.text-area:focus { border-color: var(--border-hover); }
.modal-nav { display: flex; align-items: center; justify-content: space-between; padding: 0 24px 24px; }
.nav-back { padding: 10px 18px; border-radius: 10px; border: 1px solid var(--border); background: none; color: var(--text-muted); font-size: 13px; font-weight: 500; font-family: inherit; cursor: pointer; transition: all 0.15s; }
.nav-back:hover { border-color: var(--border-hover); color: var(--text-strong); }
.nav-next { display: flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 10px; border: none; background: rgba(255,255,255,0.08); color: var(--text-heading); font-size: 13px; font-weight: 600; font-family: inherit; cursor: pointer; transition: all 0.2s var(--ease-spring); }
.nav-next:hover { background: rgba(255,255,255,0.12); }
.nav-next.final { background: rgba(52,211,153,0.2); color: #34d399; }
.nav-next.final:hover { background: rgba(52,211,153,0.3); }

/* Processing */
.processing { padding: 48px 24px; text-align: center; }
.proc-icon { margin-bottom: 16px; color: var(--text-muted); }
.proc-spinner { animation: spin 2s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.proc-title { font-family: var(--serif); font-size: 22px; color: var(--text-heading); margin-bottom: 28px; }
.proc-steps { display: flex; flex-direction: column; gap: 12px; max-width: 240px; margin: 0 auto; text-align: left; }
.proc-step { display: flex; align-items: center; gap: 10px; transition: opacity 0.3s; }
.proc-step:not(.done):not(.active) { opacity: 0.3; }
.proc-check { width: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.proc-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--text-muted); }
.proc-dot-inactive { background: var(--border); }
.proc-step.active .proc-dot { background: #fbbf24; animation: pulse 1s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.proc-step-label { font-size: 13px; color: var(--text); }
.proc-step.done .proc-step-label { color: var(--text-strong); }

/* Results */
.results { padding: 24px; }
.results-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.results-badge { font-size: 11px; font-weight: 600; color: #34d399; background: rgba(52,211,153,0.12); padding: 4px 12px; border-radius: 6px; }
.results-title { font-family: var(--serif); font-size: 24px; color: var(--text-heading); margin-bottom: 24px; }

.results-scores { display: flex; gap: 20px; justify-content: center; margin-bottom: 24px; }
.res-score { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.res-ring { position: relative; width: 56px; height: 56px; }
.res-ring svg { display: block; }
.res-num { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums; }
.res-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
.res-avg { margin-left: 4px; padding-left: 16px; border-left: 1px solid var(--border); }

.results-text { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding-top: 20px; border-top: 1px solid var(--border); margin-bottom: 20px; }
.res-block-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #34d399; margin-bottom: 6px; }
.res-block-text { font-size: 13px; line-height: 1.6; color: var(--text); }

/* AI Analysis */
.results-ai { margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
.ai-summary { font-size: 14px; line-height: 1.6; color: var(--text-strong); margin-bottom: 10px; }
.ai-tags { display: flex; gap: 5px; flex-wrap: wrap; }
.ai-tag { font-size: 10px; font-weight: 600; color: #34d399; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); padding: 3px 8px; border-radius: 5px; }

.res-highlights { margin-top: 8px; border-radius: 8px; padding: 8px 12px; }
.hl-g { background: rgba(52,211,153,0.06); }
.hl-a { background: rgba(251,191,36,0.05); }
.res-highlights ul { list-style: none; display: flex; flex-direction: column; gap: 3px; }
.res-highlights li { font-size: 11px; color: var(--text-strong); padding-left: 10px; position: relative; }
.res-highlights li::before { content: '→'; position: absolute; left: 0; font-size: 10px; }
.hl-g li::before { color: #34d399; }
.hl-a li::before { color: #fbbf24; }

.ai-advice { display: flex; align-items: flex-start; gap: 8px; padding: 12px; border-radius: 10px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); margin-bottom: 16px; }
.advice-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }
.ai-advice p { font-size: 13px; line-height: 1.5; color: var(--text); }

.results-hint { font-size: 11px; color: var(--text-muted); text-align: center; margin-bottom: 16px; }

.results-close {
  width: 100%; padding: 12px; border-radius: 10px; border: none;
  background: rgba(255,255,255,0.06); color: var(--text-heading);
  font-size: 14px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
}
.results-close:hover { background: rgba(255,255,255,0.1); }
</style>
