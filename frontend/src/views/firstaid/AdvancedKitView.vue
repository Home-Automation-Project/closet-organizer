<template>
  <div>
    <RouterLink to="/firstaid" class="text-muted text-sm">← First Aid Hub</RouterLink>
    <h1 class="page-title mt-3">Advanced First Aid Kit</h1>
    <p class="text-muted text-sm mb-4">Controlled-access kit. Divided into labelled sub-bins.</p>

    <div class="bins-selector mb-4">
      <button
        v-for="bin in bins"
        :key="bin"
        class="bin-btn"
        :class="{ active: selectedBin === bin }"
        @click="selectBin(bin)"
      >{{ bin }}</button>
    </div>

    <div v-if="loading" class="spinner" />
    <div v-else-if="!items.length" class="text-muted">No items in this bin.</div>
    <div v-else class="card">
      <table>
        <thead>
          <tr>
            <th>Item</th>
            <th>Category</th>
            <th>Qty</th>
            <th>Expires?</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="font-bold">{{ item.name }}</td>
            <td class="text-muted">{{ item.category }}</td>
            <td>{{ item.recommended_qty }} {{ item.unit }}</td>
            <td>{{ item.has_expiration ? '✓' : '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdvancedBins, getAdvancedKit } from '@/api'

const bins = ref([])
const selectedBin = ref(null)
const items = ref([])
const loading = ref(false)

async function selectBin(bin) {
  selectedBin.value = bin
  loading.value = true
  items.value = (await getAdvancedKit(bin)).data
  loading.value = false
}

onMounted(async () => {
  bins.value = (await getAdvancedBins()).data
  if (bins.value.length) await selectBin(bins.value[0])
})
</script>

<style scoped>
.bins-selector { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.bin-btn {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  padding: 0.4rem 0.9rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.bin-btn.active, .bin-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}
</style>
