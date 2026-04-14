<script setup>
import { ref, onMounted, computed } from 'vue'

const props = defineProps({ journal: String })

const manifest = ref({ work: [], daily: [] })
const search = ref('')

onMounted(async () => {
  const res = await fetch('/manifest.json')
  manifest.value = await res.json()
})

const entries = computed(() => {
  const list = manifest.value[props.journal] || []
  if (!search.value) return list
  const q = search.value.toLowerCase()
  return list.filter(
    (e) =>
      e.date.includes(q) ||
      e.day.toLowerCase().includes(q) ||
      e.summary.toLowerCase().includes(q)
  )
})

const title = computed(() =>
  props.journal === 'work' ? 'Work Journal' : 'Daily Journal'
)

const description = computed(() =>
  props.journal === 'work'
    ? 'Claude Code sessions, git activity, and project work.'
    : 'Terminal commands, file changes, and development activity.'
)
</script>

<template>
  <div class="journal">
    <div class="header">
      <div>
        <h1>{{ title }}</h1>
        <p class="desc">{{ description }}</p>
      </div>
      <input
        v-model="search"
        type="text"
        placeholder="Filter by date, day, or keyword..."
        class="search"
      />
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Day</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in entries"
            :key="entry.date"
            @click="$router.push(`/${journal}/${entry.date}`)"
          >
            <td class="date-cell">{{ entry.date }}</td>
            <td class="day-cell">{{ entry.day }}</td>
            <td class="summary-cell">
              {{ entry.summary.slice(0, 120) }}{{ entry.summary.length > 120 ? '...' : '' }}
            </td>
          </tr>
          <tr v-if="!entries.length">
            <td colspan="3" class="empty">No entries found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.journal {
  padding-top: 0.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
  margin-bottom: 0.25rem;
}

.desc {
  font-size: 0.8125rem;
  color: #71717a;
}

.search {
  background: #18181b;
  border: 1px solid #27272a;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  color: #e4e4e7;
  width: 260px;
  outline: none;
  font-family: inherit;
  flex-shrink: 0;
}

.search::placeholder {
  color: #52525b;
}

.search:focus {
  border-color: #3f3f46;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead th {
  text-align: left;
  padding: 0.625rem 0.75rem;
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
  color: #52525b;
  border-bottom: 1px solid #27272a;
}

tbody tr {
  cursor: pointer;
  transition: background 0.1s;
}

tbody tr:hover {
  background: #18181b;
}

td {
  padding: 0.75rem;
  font-size: 0.8125rem;
  border-bottom: 1px solid #1c1c1f;
  vertical-align: top;
}

.date-cell {
  font-weight: 500;
  color: #e4e4e7;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  width: 110px;
}

.day-cell {
  color: #71717a;
  white-space: nowrap;
  width: 90px;
}

.summary-cell {
  color: #a1a1aa;
  line-height: 1.5;
}

.empty {
  text-align: center;
  color: #52525b;
  padding: 2rem;
  font-style: italic;
}

@media (max-width: 600px) {
  .header {
    flex-direction: column;
    gap: 1rem;
  }
  .search {
    width: 100%;
  }
}
</style>
