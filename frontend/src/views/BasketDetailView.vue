<template>
  <div>
    <RouterLink to="/" class="text-muted text-sm">← Dashboard</RouterLink>

    <div v-if="store.loading" class="spinner mt-4" />
    <div v-else-if="store.error" class="text-muted mt-4">Error: {{ store.error }}</div>

    <template v-else-if="store.basket">
      <div class="flex items-center justify-between mt-3 mb-4">
        <div>
          <h1 class="page-title" style="margin-bottom:0.2rem">{{ store.basket.label }}</h1>
          <div class="flex gap-2 items-center">
            <span class="badge" :class="statusBadge">{{ store.basket.status }}</span>
            <span class="text-muted text-sm">{{ store.basket.basket_type }}<span v-if="store.basket.sub_bin"> · {{ store.basket.sub_bin }}</span></span>
          </div>
        </div>
        <div class="flex gap-2">
          <img :src="`/api/inventory/basket/${id}/qr.png`" alt="QR" style="width:72px;height:72px;border-radius:6px" />
        </div>
      </div>

      <InventoryTable
        :items="store.basket.inventory"
        :editable="true"
        @update-qty="handleQtyUpdate"
        @edit-item="openEditModal"
        @remove-item="handleRemove"
      />

      <button class="btn-primary mt-4" @click="openAddModal">+ Add Item</button>
    </template>

    <!-- Edit/Add Item Modal -->
    <AppModal
      :show="modal.show"
      :title="modal.editing ? 'Edit Item' : 'Add Item'"
      @close="modal.show = false"
      @confirm="saveItem"
    >
      <div v-if="!modal.editing" class="mb-3">
        <label class="label">Item Definition ID</label>
        <input class="input" type="number" v-model.number="modal.item_definition_id" placeholder="Item definition ID" />
      </div>
      <div class="mb-3">
        <label class="label">Quantity</label>
        <input class="input" type="number" min="0" v-model.number="modal.quantity" />
      </div>
      <div class="mb-3">
        <label class="label">Expiration Date (if applicable)</label>
        <input class="input" type="date" v-model="modal.expiration_date" />
      </div>
      <div>
        <label class="label">Notes</label>
        <input class="input" v-model="modal.notes" />
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { onMounted, computed, reactive } from 'vue'
import { useInventoryStore } from '@/stores/inventory'
import InventoryTable from '@/components/InventoryTable.vue'
import AppModal from '@/components/AppModal.vue'

const props = defineProps({ id: { type: String, required: true } })
const store = useInventoryStore()

const statusBadge = computed(() => {
  const s = store.basket?.status
  if (s === 'RED') return 'badge-red'
  if (s === 'YELLOW') return 'badge-yellow'
  return 'badge-green'
})

const modal = reactive({
  show: false, editing: false,
  item_definition_id: null, inventory_id: null,
  quantity: 0, expiration_date: '', notes: '',
})

function openEditModal(item) {
  modal.editing = true
  modal.item_definition_id = item.item_definition_id
  modal.inventory_id = item.id
  modal.quantity = item.quantity
  modal.expiration_date = item.expiration_date ? item.expiration_date.substring(0, 10) : ''
  modal.notes = item.notes || ''
  modal.show = true
}

function openAddModal() {
  modal.editing = false
  modal.item_definition_id = null
  modal.quantity = 1
  modal.expiration_date = ''
  modal.notes = ''
  modal.show = true
}

async function saveItem() {
  const data = {
    quantity: modal.quantity,
    expiration_date: modal.expiration_date || null,
    notes: modal.notes || null,
  }
  await store.updateItem(+props.id, modal.item_definition_id, data)
  await store.fetchBasket(+props.id)
  modal.show = false
}

async function handleQtyUpdate(item, newQty) {
  await store.updateItem(+props.id, item.item_definition_id, { quantity: newQty })
  await store.fetchBasket(+props.id)
}

async function handleRemove(item) {
  if (confirm(`Remove "${item.item_definition.name}" from inventory?`)) {
    await store.removeItem(item.id)
  }
}

onMounted(() => store.fetchBasket(+props.id))
</script>
