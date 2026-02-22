<template>
  <div class="scan-wrapper">
    <div v-if="store.loading" class="spinner mt-4" />
    <div v-else-if="store.error" class="card text-muted" style="text-align:center;padding:2rem">
      ❌ Basket not found or invalid QR code.
    </div>

    <template v-else-if="store.basket">
      <div class="scan-header">
        <div class="type-icon">{{ typeIcon }}</div>
        <div>
          <h1 style="font-size:1.4rem;font-weight:700">{{ store.basket.label }}</h1>
          <div class="flex items-center gap-2 mt-1">
            <span class="badge" :class="statusBadge">{{ store.basket.status }}</span>
            <span class="text-muted text-sm">{{ store.basket.basket_type }}<span v-if="store.basket.sub_bin"> · {{ store.basket.sub_bin }}</span></span>
          </div>
        </div>
      </div>

      <div class="card mt-4">
        <div class="section-title">Inventory</div>
        <div v-if="!store.basket.inventory.length" class="text-muted text-sm">No items tracked.</div>
        <div
          v-for="item in store.basket.inventory"
          :key="item.id"
          class="scan-item"
        >
          <div class="scan-item-name">{{ item.item_definition.name }}</div>
          <div class="flex items-center gap-2 mt-1">
            <span class="badge" :class="qtyBadge(item.quantity_status)">
              {{ item.quantity }} / {{ item.item_definition.recommended_qty }} {{ item.item_definition.unit }}
            </span>
            <span v-if="item.item_definition.has_expiration && item.expiration_date"
              class="badge" :class="expBadge(item.expiration_status)">
              Exp: {{ fmtDate(item.expiration_date) }}
            </span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useInventoryStore } from '@/stores/inventory'

const props = defineProps({ token: { type: String, required: true } })
const store = useInventoryStore()

const statusBadge = computed(() => {
  const s = store.basket?.status
  if (s === 'RED') return 'badge-red'
  if (s === 'YELLOW') return 'badge-yellow'
  return 'badge-green'
})
const typeIcon = computed(() => {
  const t = store.basket?.basket_type
  if (t === 'BEDDING') return '🛏️'
  if (t === 'CLEANING') return '🧹'
  if (t === 'FIRST_AID_BASIC') return '🩹'
  if (t === 'FIRST_AID_ADVANCED') return '🚑'
  return '📦'
})

function fmtDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
function qtyBadge(s) {
  if (s === 'LOW') return 'badge-yellow'
  if (s === 'OVERSTOCKED') return 'badge-gray'
  return 'badge-green'
}
function expBadge(s) {
  if (s === 'EXPIRED') return 'badge-red'
  if (s === 'EXPIRING_SOON') return 'badge-yellow'
  return 'badge-green'
}

onMounted(() => store.fetchByToken(props.token))
</script>

<style scoped>
.scan-wrapper { max-width: 480px; margin: 0 auto; }
.scan-header { display: flex; align-items: center; gap: 1rem; margin-top: 1rem; }
.type-icon { font-size: 2.5rem; }
.scan-item { padding: 0.75rem 0; border-bottom: 1px solid var(--color-border); }
.scan-item:last-child { border-bottom: none; }
.scan-item-name { font-weight: 600; font-size: 0.95rem; }
</style>
