<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { marked } from 'marked'

const props = defineProps({ journal: String, date: String })

const content = ref('')
const loading = ref(true)
const manifest = ref({ work: [], daily: [] })

const title = computed(() =>
  props.journal === 'work' ? 'Work Journal' : 'Daily Journal'
)

const rendered = computed(() => {
  if (!content.value) return ''
  return marked(content.value)
})

const entries = computed(() => manifest.value[props.journal] || [])

const currentIndex = computed(() =>
  entries.value.findIndex((e) => e.date === props.date)
)

const prevEntry = computed(() => {
  const i = currentIndex.value
  return i < entries.value.length - 1 ? entries.value[i + 1] : null
})

const nextEntry = computed(() => {
  const i = currentIndex.value
  return i > 0 ? entries.value[i - 1] : null
})

async function loadEntry() {
  loading.value = true
  try {
    const res = await fetch(`/entries/${props.journal}/${props.date}.md`)
    if (res.ok) {
      content.value = await res.text()
    } else {
      content.value = `# Not Found\n\nNo entry for ${props.date}.`
    }
  } catch {
    content.value = `# Error\n\nCould not load entry.`
  }
  loading.value = false
}

onMounted(async () => {
  const res = await fetch('/manifest.json')
  manifest.value = await res.json()
  loadEntry()
})

watch(() => props.date, loadEntry)
</script>

<template>
  <div class="entry-page">
    <div class="breadcrumb">
      <router-link :to="`/${journal}`" class="back">{{ title }}</router-link>
      <span class="sep">/</span>
      <span class="current">{{ date }}</span>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <article v-else class="prose" v-html="rendered" />

    <div class="nav-footer">
      <router-link
        v-if="prevEntry"
        :to="`/${journal}/${prevEntry.date}`"
        class="nav-btn prev"
      >
        <span class="nav-label">Previous</span>
        <span class="nav-date">{{ prevEntry.date }}</span>
      </router-link>
      <div v-else />

      <router-link
        v-if="nextEntry"
        :to="`/${journal}/${nextEntry.date}`"
        class="nav-btn next"
      >
        <span class="nav-label">Next</span>
        <span class="nav-date">{{ nextEntry.date }}</span>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.entry-page {
  padding-top: 0.5rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.8125rem;
}

.back {
  color: #71717a;
  transition: color 0.15s;
}

.back:hover {
  color: #e4e4e7;
}

.sep {
  color: #3f3f46;
}

.current {
  color: #a1a1aa;
}

.loading {
  color: #52525b;
  padding: 3rem;
  text-align: center;
}

/* Markdown prose styling */
.prose :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
  margin-bottom: 1rem;
}

.prose :deep(h2) {
  font-size: 1.125rem;
  font-weight: 600;
  color: #d4d4d8;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #1c1c1f;
}

.prose :deep(h3) {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #a1a1aa;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(blockquote) {
  border-left: 3px solid #3f3f46;
  padding-left: 1rem;
  color: #a1a1aa;
  margin: 1rem 0;
  font-style: italic;
  line-height: 1.7;
  font-size: 0.9375rem;
}

.prose :deep(p) {
  margin: 0.5rem 0;
  line-height: 1.7;
  font-size: 0.875rem;
  color: #d4d4d8;
}

.prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.8125rem;
}

.prose :deep(th) {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #52525b;
  border-bottom: 1px solid #27272a;
  font-weight: 600;
}

.prose :deep(td) {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #1c1c1f;
  color: #a1a1aa;
}

.prose :deep(ul),
.prose :deep(ol) {
  padding-left: 1.25rem;
  margin: 0.5rem 0;
}

.prose :deep(li) {
  margin: 0.375rem 0;
  font-size: 0.8125rem;
  color: #a1a1aa;
  line-height: 1.6;
}

.prose :deep(code) {
  background: #1c1c1f;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  font-size: 0.8em;
  color: #e4e4e7;
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
}

.prose :deep(hr) {
  border: none;
  border-top: 1px solid #27272a;
  margin: 2rem 0;
}

.prose :deep(em) {
  color: #71717a;
}

.prose :deep(strong) {
  color: #e4e4e7;
  font-weight: 600;
}

/* Navigation footer */
.nav-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid #1c1c1f;
}

.nav-btn {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid #27272a;
  transition: all 0.15s;
}

.nav-btn:hover {
  border-color: #3f3f46;
  background: #18181b;
}

.nav-btn.next {
  text-align: right;
  margin-left: auto;
}

.nav-label {
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #52525b;
}

.nav-date {
  font-size: 0.875rem;
  font-weight: 500;
  color: #e4e4e7;
  font-variant-numeric: tabular-nums;
}
</style>
