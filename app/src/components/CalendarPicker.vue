<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: String,       // YYYY-MM-DD
  availableDates: Array,    // ['2026-04-14', ...]
  brandColor: { type: String, default: '#6395ff' },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)

// Parse current date
const currentDate = computed(() => {
  if (!props.modelValue) return new Date()
  return new Date(props.modelValue + 'T12:00:00')
})

// Viewed month (can navigate independently)
const viewYear = ref(currentDate.value.getFullYear())
const viewMonth = ref(currentDate.value.getMonth())

watch(currentDate, (d) => {
  viewYear.value = d.getFullYear()
  viewMonth.value = d.getMonth()
})

const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const dayNames = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

const viewLabel = computed(() => `${monthNames[viewMonth.value]} ${viewYear.value}`)

// Available dates as Set for fast lookup
const available = computed(() => new Set(props.availableDates || []))

// Calendar grid
const calendarDays = computed(() => {
  const year = viewYear.value
  const month = viewMonth.value
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  // Monday = 0
  let startDow = firstDay.getDay() - 1
  if (startDow < 0) startDow = 6

  const days = []

  // Previous month padding
  const prevLast = new Date(year, month, 0).getDate()
  for (let i = startDow - 1; i >= 0; i--) {
    const d = prevLast - i
    const m = month === 0 ? 11 : month - 1
    const y = month === 0 ? year - 1 : year
    const dateStr = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ day: d, dateStr, outside: true, hasEntry: available.value.has(dateStr) })
  }

  // Current month
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({
      day: d,
      dateStr,
      outside: false,
      today: dateStr === new Date().toISOString().slice(0, 10),
      selected: dateStr === props.modelValue,
      hasEntry: available.value.has(dateStr),
    })
  }

  // Next month padding
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    const m = month === 11 ? 0 : month + 1
    const y = month === 11 ? year + 1 : year
    const dateStr = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ day: d, dateStr, outside: true, hasEntry: available.value.has(dateStr) })
  }

  return days
})

function prevMonth() {
  if (viewMonth.value === 0) { viewMonth.value = 11; viewYear.value-- }
  else viewMonth.value--
}
function nextMonth() {
  if (viewMonth.value === 11) { viewMonth.value = 0; viewYear.value++ }
  else viewMonth.value++
}

function selectDate(day) {
  if (!day.hasEntry) return
  emit('update:modelValue', day.dateStr)
  open.value = false
}

function toggle() { open.value = !open.value }

// Close on outside click
const wrapper = ref(null)
function onClickOutside(e) {
  if (wrapper.value && !wrapper.value.contains(e.target)) open.value = false
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="cal-wrapper" ref="wrapper">
    <!-- Trigger button -->
    <button class="cal-trigger" @click="toggle" title="Pick date">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
    </button>

    <!-- Dropdown -->
    <Transition name="fade">
      <div v-if="open" class="cal-dropdown" @click.stop>
        <!-- Month nav -->
        <div class="cal-header">
          <button class="cal-nav" @click="prevMonth">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </button>
          <span class="cal-month">{{ viewLabel }}</span>
          <button class="cal-nav" @click="nextMonth">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </button>
        </div>

        <!-- Day names -->
        <div class="cal-weekdays">
          <span v-for="d in dayNames" :key="d" class="cal-weekday">{{ d }}</span>
        </div>

        <!-- Days grid -->
        <div class="cal-grid">
          <button
            v-for="(day, i) in calendarDays"
            :key="i"
            :class="[
              'cal-day',
              { outside: day.outside },
              { today: day.today },
              { selected: day.selected },
              { 'has-entry': day.hasEntry },
              { disabled: !day.hasEntry },
            ]"
            @click="selectDate(day)"
            :disabled="!day.hasEntry"
          >
            <span>{{ day.day }}</span>
            <span v-if="day.hasEntry && !day.outside" class="cal-dot" :style="{ background: brandColor }"></span>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.cal-wrapper { position: relative; }

.cal-trigger {
  display: flex; align-items: center; justify-content: center;
  width: 40px; height: 40px; border-radius: 10px;
  border: 1px solid var(--border); background: rgba(12,12,14,0.7);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  color: var(--text);
  font-family: inherit; cursor: pointer;
  transition: all 0.2s var(--ease-spring, cubic-bezier(0.16,1,0.3,1));
}
.cal-trigger:hover { border-color: var(--border-hover); color: var(--text-heading); background: rgba(12,12,14,0.85); }
.cal-date-text { display: none; }

.cal-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  width: 280px; padding: 16px;
  background: rgba(18, 18, 22, 0.95);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border); border-radius: 14px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 2px 8px rgba(0,0,0,0.3);
  z-index: 9999;
}

.cal-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px;
}
.cal-month {
  font-family: var(--serif); font-size: 15px; color: var(--text-heading);
}
.cal-nav {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 7px;
  border: none; background: none; color: var(--text-muted);
  cursor: pointer; transition: all 0.15s;
}
.cal-nav:hover { background: var(--bg-elevated); color: var(--text-strong); }

.cal-weekdays {
  display: grid; grid-template-columns: repeat(7, 1fr);
  margin-bottom: 4px;
}
.cal-weekday {
  text-align: center; font-size: 10px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--text-muted); padding: 4px 0;
}

.cal-grid {
  display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px;
}

.cal-day {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 34px; border-radius: 8px;
  border: none; background: none;
  font-size: 12px; font-weight: 500; font-family: inherit;
  font-variant-numeric: tabular-nums;
  color: var(--text-strong); cursor: pointer;
  transition: all 0.12s; position: relative;
}
.cal-day:hover:not(.disabled) { background: var(--bg-elevated); }
.cal-day.outside { color: var(--border-hover); }
.cal-day.disabled { cursor: default; color: var(--border-hover); opacity: 0.5; }
.cal-day.today { color: var(--text-heading); font-weight: 700; }
.cal-day.today::after {
  content: ''; position: absolute; bottom: 2px;
  width: 3px; height: 3px; border-radius: 50%;
  background: var(--text-heading);
}
.cal-day.selected {
  background: v-bind(brandColor);
  color: #0c0c0e; font-weight: 700;
}
.cal-day.selected:hover { opacity: 0.9; }

.cal-dot {
  width: 4px; height: 4px; border-radius: 50%;
  position: absolute; bottom: 3px;
}
.cal-day.selected .cal-dot { background: rgba(0,0,0,0.4) !important; }

/* Transition */
.fade-enter-active, .fade-leave-active { transition: all 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
