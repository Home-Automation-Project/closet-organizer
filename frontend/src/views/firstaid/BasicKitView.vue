<template>
  <div>
    <RouterLink to="/firstaid" class="text-muted text-sm">← First Aid Hub</RouterLink>
    <h1 class="page-title mt-3">Basic First Aid Kit</h1>

    <div v-if="!items.length" class="spinner" />
    <div v-else>
      <div v-for="[cat, catItems] in categories" :key="cat" class="card mb-4">
        <div class="section-title">{{ cat }}</div>
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Qty</th>
              <th>Expires?</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in catItems" :key="item.id">
              <td>{{ item.name }}</td>
              <td>{{ item.recommended_qty }} {{ item.unit }}</td>
              <td>{{ item.has_expiration ? '✓' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getBasicKit } from '@/api'

const items = ref([])
const categories = computed(() => {
  const map = new Map()
  for (const item of items.value) {
    const cat = item.category || 'General'
    if (!map.has(cat)) map.set(cat, [])
    map.get(cat).push(item)
  }
  return [...map.entries()]
})
onMounted(async () => { items.value = (await getBasicKit()).data })
</script>
