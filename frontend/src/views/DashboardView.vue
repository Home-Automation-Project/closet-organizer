<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="page-title" style="margin-bottom:0">Dashboard</h1>
      <RouterLink to="/setup" class="btn-ghost" style="font-size:0.875rem;padding:0.4rem 0.9rem">
        + Manage Closets
      </RouterLink>
    </div>

    <div v-if="store.loading" class="spinner" />
    <div v-else-if="store.error" class="text-muted">Error: {{ store.error }}</div>
    <div v-else-if="!store.closets.length" class="card text-muted" style="text-align:center;padding:3rem">
      No closets configured yet.
      <RouterLink to="/setup" style="display:block;margin-top:0.75rem">Set up your first closet →</RouterLink>
    </div>

    <div v-else class="closets-grid">
      <div
        v-for="closet in store.closets"
        :key="closet.id"
        class="card closet-card"
      >
        <div class="closet-header">
          <div>
            <div class="font-bold">{{ closet.name }}</div>
            <div class="text-muted text-sm">{{ closet.location }}</div>
          </div>
          <button class="btn-ghost" style="font-size:0.78rem" @click="loadCloset(closet.id)">Refresh</button>
        </div>

        <div v-if="closetDetails[closet.id]">
          <div
            v-for="shelf in closetDetails[closet.id].shelves"
            :key="shelf.id"
            class="shelf-row"
          >
            <div class="shelf-label">{{ shelf.label || `Shelf ${shelf.position_order + 1}` }}</div>
            <div class="baskets-row">
              <BasketIcon
                v-for="basket in shelf.baskets"
                :key="basket.id"
                :basket="basket"
              />
              <div v-if="!shelf.baskets.length" class="text-muted text-sm" style="padding:0.5rem">
                Empty shelf
              </div>
            </div>
          </div>
          <div v-if="!closetDetails[closet.id].shelves.length" class="text-muted text-sm" style="padding:0.5rem">
            No shelves configured.
          </div>
        </div>
        <div v-else class="spinner" style="width:24px;height:24px;margin:1rem auto" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useClosetStore } from '@/stores/closets'
import { getCloset } from '@/api'
import BasketIcon from '@/components/BasketIcon.vue'

const store = useClosetStore()
const closetDetails = reactive({})

async function loadCloset(id) {
  try {
    const res = await getCloset(id)
    closetDetails[id] = res.data
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  await store.fetchClosets()
  for (const c of store.closets) await loadCloset(c.id)
})
</script>

<style scoped>
.closets-grid { display: flex; flex-direction: column; gap: 1.25rem; }
.closet-card { padding: 1rem; }
.closet-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.shelf-row { margin-bottom: 1rem; }
.shelf-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
  margin-bottom: 0.5rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--color-border);
}
.baskets-row { display: flex; flex-wrap: wrap; gap: 0.75rem; }
</style>
