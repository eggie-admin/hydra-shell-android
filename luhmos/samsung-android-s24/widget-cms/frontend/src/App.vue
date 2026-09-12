<script setup>
import { computed, onMounted, ref } from 'vue'

const apiBase = import.meta.env.VITE_API_BASE || ''
const pages = ref([])
const selectedSlug = ref('')
const adminToken = ref('')
const status = ref('Idle')
const form = ref({ slug: '', title: '', body: '', pageStatus: 'draft', metadata: '{}' })

const selectedPage = computed(() => pages.value.find((page) => page.slug === selectedSlug.value) || null)

async function loadPages() {
  status.value = 'Loading pages...'
  const res = await fetch(`${apiBase}/api/pages`)
  if (!res.ok) throw new Error(`Load failed: ${res.status}`)
  pages.value = await res.json()
  if (!selectedSlug.value && pages.value.length) selectPage(pages.value[0])
  status.value = `Loaded ${pages.value.length} page(s)`
}

function selectPage(page) {
  selectedSlug.value = page.slug
  form.value = {
    slug: page.slug,
    title: page.title,
    body: page.body,
    pageStatus: page.status,
    metadata: JSON.stringify(page.metadata || {}, null, 2),
  }
}

function newPage() {
  selectedSlug.value = ''
  form.value = { slug: '', title: '', body: '', pageStatus: 'draft', metadata: '{}' }
  status.value = 'New page draft ready'
}

function parseMetadata() {
  try {
    return JSON.parse(form.value.metadata || '{}')
  } catch {
    throw new Error('Metadata must be valid JSON')
  }
}

async function savePage() {
  const payload = {
    title: form.value.title.trim(),
    body: form.value.body.trim(),
    status: form.value.pageStatus,
    metadata: parseMetadata(),
  }
  if (!payload.title || !payload.body) throw new Error('Title and body are required')
  if (!adminToken.value) throw new Error('Admin token required')

  const headers = { 'Content-Type': 'application/json', 'X-KAI-Admin': adminToken.value }
  let res
  if (selectedSlug.value) {
    res = await fetch(`${apiBase}/api/pages/${selectedSlug.value}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(payload),
    })
  } else {
    const slug = form.value.slug.trim()
    if (!/^[a-z0-9][a-z0-9-]{0,80}$/.test(slug)) throw new Error('Slug must be lowercase kebab-case')
    res = await fetch(`${apiBase}/api/pages`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ slug, ...payload }),
    })
  }
  if (!res.ok) throw new Error(`Save failed: ${res.status}`)
  const saved = await res.json()
  await loadPages()
  selectPage(saved)
  status.value = `Saved ${saved.slug}`
}

async function deletePage() {
  if (!selectedSlug.value) return
  if (!adminToken.value) throw new Error('Admin token required')
  const res = await fetch(`${apiBase}/api/pages/${selectedSlug.value}`, {
    method: 'DELETE',
    headers: { 'X-KAI-Admin': adminToken.value },
  })
  if (!res.ok) throw new Error(`Delete failed: ${res.status}`)
  selectedSlug.value = ''
  await loadPages()
  status.value = 'Page deleted'
}

async function run(action) {
  try {
    await action()
  } catch (err) {
    status.value = err.message || String(err)
  }
}

onMounted(() => run(loadPages))
</script>

<template>
  <main class="shell">
    <section class="hero">
      <div>
        <p class="eyebrow">KAI-owned CMS mutation</p>
        <h1>Vue cockpit, FastAPI spine, no donor sludge.</h1>
        <p class="lede">Chrome Dev and Canary stay in the lab as behavior harnesses. This app stays clean.</p>
      </div>
      <button type="button" @click="run(loadPages)">Refresh</button>
    </section>

    <section class="grid">
      <aside class="panel">
        <div class="row between">
          <h2>Pages</h2>
          <button type="button" @click="newPage">New</button>
        </div>
        <button
          v-for="page in pages"
          :key="page.slug"
          type="button"
          class="page-button"
          :class="{ active: page.slug === selectedSlug }"
          @click="selectPage(page)"
        >
          <strong>{{ page.title }}</strong>
          <span>{{ page.slug }} · {{ page.status }}</span>
        </button>
      </aside>

      <section class="panel editor">
        <label>
          Admin token
          <input v-model="adminToken" type="password" autocomplete="off" placeholder="KAI_ADMIN_TOKEN" />
        </label>
        <label>
          Slug
          <input v-model="form.slug" :disabled="Boolean(selectedSlug)" placeholder="source-of-truth" />
        </label>
        <label>
          Title
          <input v-model="form.title" placeholder="Page title" />
        </label>
        <label>
          Body
          <textarea v-model="form.body" rows="9" placeholder="Write the CMS page body..."></textarea>
        </label>
        <label>
          Status
          <select v-model="form.pageStatus">
            <option value="draft">draft</option>
            <option value="published">published</option>
            <option value="archived">archived</option>
          </select>
        </label>
        <label>
          Metadata JSON
          <textarea v-model="form.metadata" rows="5"></textarea>
        </label>
        <div class="row actions">
          <button type="button" @click="run(savePage)">Save page</button>
          <button type="button" class="danger" :disabled="!selectedPage" @click="run(deletePage)">Delete</button>
        </div>
        <p class="status" aria-live="polite">{{ status }}</p>
      </section>
    </section>
  </main>
</template>
