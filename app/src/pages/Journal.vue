<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ journal: String })
const router = useRouter()
const manifest = ref({ work: [], daily: [] })
const search = ref('')

onMounted(async () => { manifest.value = await (await fetch('/manifest.json')).json() })

const entries = computed(() => manifest.value[props.journal] || [])
const filtered = computed(() => {
  if (!search.value) return entries.value
  const q = search.value.toLowerCase()
  return entries.value.filter(e => e.date.includes(q) || e.day.toLowerCase().includes(q) || e.summary.toLowerCase().includes(q))
})
const title = computed(() => props.journal === 'work' ? 'Work Journal' : 'Daily Journal')
const desc = computed(() => props.journal === 'work' ? 'Claude sessions & git activity' : 'Terminal, files & development')
</script>

<template>
  <div class="page">
    <!-- Sub-header -->
    <div class="subheader">
      <div class="mx header-inner">
        <div class="header-left">
          <router-link to="/" class="back-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </router-link>
          <div>
            <p class="label">{{ title }}</p>
            <h1 class="htitle">{{ desc }}</h1>
          </div>
        </div>
        <button v-if="entries.length" class="latest-btn" @click="router.push(`/${journal}/${entries[0]?.date}`)">Latest</button>
      </div>
    </div>

    <div class="mx body">
      <div class="search-wrap">
        <input v-model="search" type="text" placeholder="Filter by date, day, or keyword..." class="search" />
        <span class="count">{{ filtered.length }} entries</span>
      </div>

      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Day</th>
            <th v-if="journal==='work'" class="th-n">S</th>
            <th v-if="journal==='work'" class="th-n">C</th>
            <th v-if="journal==='daily'" class="th-n">Cmd</th>
            <th v-if="journal==='daily'" class="th-n">C</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in filtered" :key="e.date" @click="router.push(`/${journal}/${e.date}`)">
            <td class="td-date">{{ e.date }}</td>
            <td class="td-day">{{ e.day?.slice(0, 3) }}</td>
            <td class="td-n" v-if="journal==='work'">{{ e.stats?.sessions || 0 }}</td>
            <td class="td-n" v-if="journal==='work'">{{ e.stats?.commits || 0 }}</td>
            <td class="td-n" v-if="journal==='daily'">{{ e.stats?.commands || 0 }}</td>
            <td class="td-n" v-if="journal==='daily'">{{ e.stats?.commits || 0 }}</td>
            <td class="td-summary">{{ e.summary }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { min-height: calc(100vh - 52px); }
.subheader { border-bottom: 1px solid var(--border); background: var(--bg-card); padding: 20px 0; }
.mx { max-width: 880px; margin: 0 auto; padding-left: 24px; padding-right: 24px; }
.header-inner { display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 12px; }
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--border);
  color: var(--text-muted); transition: all 0.15s; flex-shrink: 0;
}
.back-btn:hover { border-color: var(--border-hover); color: var(--text-strong); }
.label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em; color: var(--text-muted); }
.htitle { margin-top: 2px; font-size: 16px; font-weight: 700; letter-spacing: -0.02em; color: var(--text-heading); }
.latest-btn { font-size: 12px; font-weight: 500; color: var(--bg); background: var(--text-strong); padding: 6px 14px; border-radius: 8px; border: none; cursor: pointer; font-family: inherit; }

.body { padding: 16px 0 64px; }
.search-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.search { flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; font-size: 13px; color: var(--text-strong); outline: none; font-family: inherit; }
.search::placeholder { color: var(--text-muted); }
.search:focus { border-color: var(--border-hover); }
.count { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }

table { width: 100%; border-collapse: collapse; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
thead th { text-align: left; padding: 10px 12px; font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; color: var(--text-muted); border-bottom: 1px solid var(--border); }
.th-n { width: 44px; text-align: center; }
tbody tr { cursor: pointer; transition: background 0.1s; }
tbody tr:hover { background: var(--bg-elevated); }
td { padding: 10px 12px; font-size: 13px; border-bottom: 1px solid var(--border); }
.td-date { font-weight: 500; color: var(--text-strong); font-variant-numeric: tabular-nums; width: 100px; }
.td-day { color: var(--text-muted); width: 40px; }
.td-n { color: var(--text-muted); font-variant-numeric: tabular-nums; font-size: 12px; width: 44px; text-align: center; }
.td-summary { color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 400px; }
</style>
