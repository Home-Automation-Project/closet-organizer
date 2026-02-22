<template>
  <div>
    <div class="flex items-center gap-2 mb-1">
      <RouterLink to="/cleaning" class="btn-ghost btn-sm">← Rooms</RouterLink>
      <h1 class="page-title mb-0">{{ roomLabel }}</h1>
    </div>
    <p class="text-muted text-sm mb-4">Tap an item to mark it done for this session. Progress is saved locally.</p>

    <div class="flex gap-2 mb-4">
      <button class="btn-danger btn-sm" @click="handleReset">Reset Session</button>
      <span class="text-muted text-sm" style="align-self:center">
        {{ completedCount }} / {{ totalCount }} completed
      </span>
    </div>

    <div v-if="loading" class="spinner mx-auto mt-8"></div>
    <div v-else-if="error" class="text-danger text-center mt-8">{{ error }}</div>
    <div v-else>
      <div v-for="freq in orderedFrequencies" :key="freq" v-show="groupedItems[freq]?.length">
        <h2 class="section-title mt-6">{{ freqLabel(freq) }}</h2>
        <div class="checklist-list">
          <label
            v-for="item in groupedItems[freq]"
            :key="item.item_key"
            class="checklist-item"
            :class="{ done: item.completed }"
          >
            <input
              type="checkbox"
              :checked="item.completed"
              @change="handleToggle(item)"
              class="checklist-checkbox"
            />
            <span class="item-desc">{{ item.description }}</span>
            <span v-if="item.category" class="badge badge-ghost item-cat">{{ item.category }}</span>
          </label>
        </div>
      </div>
      <p v-if="totalCount === 0" class="text-muted text-center mt-8">No checklist items found for this room.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCleaningStore } from '@/stores/cleaning'

const route = useRoute()
const store = useCleaningStore()

const room = computed(() => route.params.room)
const loading = ref(false)
const error = ref(null)

const orderedFrequencies = ['DAILY', 'WEEKLY', 'MONTHLY', 'SEASONAL']

const freqLabels = { DAILY: '🔁 Daily', WEEKLY: '📅 Weekly', MONTHLY: '📆 Monthly', SEASONAL: '🌿 Seasonal' }
function freqLabel(f) { return freqLabels[f] || f }

const roomLabels = {
  library: 'Library', kitchen: 'Kitchen', dining_room: 'Dining Room', gym: 'Gym',
  bedroom: 'Bedroom', bathroom: 'Bathroom', playroom: 'Playroom', hallways: 'Hallways',
  laundry_room: 'Laundry Room', garage: 'Garage', family_room: 'Family Room',
}
const roomLabel = computed(() => roomLabels[room.value] || room.value.replace(/_/g, ' '))

// The store returns { items: [...], completions: [...], session_token: '...' }
const checklistData = computed(() => store.checklist)

const items = computed(() => {
  const data = checklistData.value
  if (!data) return []
  const completedKeys = new Set((data.completions || []).map(c => c.item_key))
  return (data.items || []).map(item => ({
    ...item,
    completed: completedKeys.has(item.item_key),
  }))
})

const groupedItems = computed(() => {
  const g = {}
  for (const item of items.value) {
    const f = item.frequency
    if (!g[f]) g[f] = []
    g[f].push(item)
  }
  return g
})

const totalCount = computed(() => items.value.length)
const completedCount = computed(() => items.value.filter(i => i.completed).length)

async function load() {
  loading.value = true
  error.value = null
  try {
    await store.fetchChecklist(room.value)
  } catch (e) {
    error.value = 'Failed to load checklist.'
  } finally {
    loading.value = false
  }
}

async function handleToggle(item) {
  // store.toggleItem(room, itemKey, isCompleted) — isCompleted is the CURRENT state
  await store.toggleItem(room.value, item.item_key, item.completed)
}

async function handleReset() {
  if (!confirm('Reset all completed items for this session?')) return
  await store.resetChecklist(room.value)
}

onMounted(load)
</script>

<style scoped>
.checklist-list { display: flex; flex-direction: column; gap: 0.25rem; }
.checklist-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 0.1s;
  min-height: 3rem;
}
.checklist-item:hover { background: var(--color-surface-hover, #1e2130); }
.checklist-item.done { opacity: 0.5; }
.checklist-item.done .item-desc { text-decoration: line-through; }
.checklist-checkbox { width: 1.25rem; height: 1.25rem; accent-color: var(--color-primary); cursor: pointer; flex-shrink: 0; }
.item-desc { flex: 1; color: var(--color-text); font-size: 0.95rem; }
.item-cat { margin-left: auto; flex-shrink: 0; font-size: 0.7rem; }
.btn-sm { font-size: 0.8rem; padding: 0.3rem 0.75rem; }
</style>
