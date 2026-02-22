<template>
  <div>
    <h1 class="page-title">Setup</h1>

    <!-- Closet list -->
    <div class="flex items-center justify-between mb-3">
      <span class="section-title" style="margin-bottom:0">Closets</span>
      <button class="btn-primary" @click="openClosetModal()">+ Add Closet</button>
    </div>

    <div v-if="!store.closets.length" class="card text-muted" style="padding:2rem;text-align:center">
      No closets yet. Add one above.
    </div>

    <div v-for="closet in store.closets" :key="closet.id" class="card mb-4">
      <!-- Closet header -->
      <div class="flex items-center justify-between mb-3">
        <div>
          <span class="font-bold">{{ closet.name }}</span>
          <span class="text-muted text-sm ml-2">{{ closet.location }}</span>
        </div>
        <div class="flex gap-2">
          <button class="btn-ghost" @click="openClosetModal(closet)">Edit</button>
          <button class="btn-danger" @click="confirmDeleteCloset(closet)">Delete</button>
        </div>
      </div>

      <!-- Shelves -->
      <div class="ml-2">
        <div class="flex items-center justify-between mb-2">
          <span class="section-title" style="margin-bottom:0">Shelves</span>
          <button class="btn-ghost" style="font-size:0.8rem" @click="openShelfModal(closet)">+ Add Shelf</button>
        </div>

        <div
          v-for="shelf in shelvesFor(closet.id)"
          :key="shelf.id"
          class="card mb-2"
          style="background:var(--color-bg)"
        >
          <div class="flex items-center justify-between mb-2">
            <span>{{ shelf.label || `Shelf ${shelf.position_order + 1}` }}</span>
            <div class="flex gap-2">
              <button class="btn-ghost" style="font-size:0.78rem" @click="openShelfModal(closet, shelf)">Edit</button>
              <button class="btn-danger" style="font-size:0.78rem" @click="confirmDeleteShelf(shelf)">Delete</button>
            </div>
          </div>

          <!-- Baskets on this shelf -->
          <div class="ml-2">
            <div class="flex items-center justify-between mb-1">
              <span class="text-muted text-sm">Baskets</span>
              <button class="btn-ghost" style="font-size:0.75rem" @click="openBasketModal(shelf)">+ Add Basket</button>
            </div>
            <div class="baskets-list">
              <div
                v-for="basket in basketsFor(shelf.id)"
                :key="basket.id"
                class="basket-row"
              >
                <span>{{ basket.label }}</span>
                <span class="badge badge-gray" style="font-size:0.65rem">{{ basket.basket_type }}</span>
                <span v-if="basket.sub_bin" class="text-muted text-sm">({{ basket.sub_bin }})</span>
                <a :href="`/api/inventory/basket/${basket.id}/qr.png`" target="_blank" class="btn-ghost"
                  style="font-size:0.72rem;padding:0.2rem 0.5rem">QR</a>
                <button class="btn-ghost" style="font-size:0.72rem;padding:0.2rem 0.5rem"
                  @click="openBasketModal(shelf, basket)">Edit</button>
                <button class="btn-danger" style="font-size:0.72rem;padding:0.2rem 0.5rem"
                  @click="confirmDeleteBasket(basket)">Del</button>
              </div>
              <div v-if="!basketsFor(shelf.id).length" class="text-muted text-sm">No baskets.</div>
            </div>
          </div>
        </div>
        <div v-if="!shelvesFor(closet.id).length" class="text-muted text-sm">No shelves configured.</div>
      </div>
    </div>

    <!-- Closet Modal -->
    <AppModal
      :show="closetModal.show"
      :title="closetModal.editing ? 'Edit Closet' : 'Add Closet'"
      @close="closetModal.show = false"
      @confirm="saveCloset"
    >
      <div class="mb-3">
        <label class="label">Name</label>
        <input class="input" v-model="closetModal.name" placeholder="e.g. Hallway Closet" />
      </div>
      <div>
        <label class="label">Location</label>
        <input class="input" v-model="closetModal.location" placeholder="e.g. Second Floor Hallway" />
      </div>
    </AppModal>

    <!-- Shelf Modal -->
    <AppModal
      :show="shelfModal.show"
      :title="shelfModal.editing ? 'Edit Shelf' : 'Add Shelf'"
      @close="shelfModal.show = false"
      @confirm="saveShelf"
    >
      <div class="mb-3">
        <label class="label">Label</label>
        <input class="input" v-model="shelfModal.label" placeholder="e.g. Top Shelf" />
      </div>
      <div>
        <label class="label">Position Order</label>
        <input class="input" type="number" min="0" v-model.number="shelfModal.position_order" />
      </div>
    </AppModal>

    <!-- Basket Modal -->
    <AppModal
      :show="basketModal.show"
      :title="basketModal.editing ? 'Edit Basket' : 'Add Basket'"
      @close="basketModal.show = false"
      @confirm="saveBasket"
    >
      <div class="mb-3">
        <label class="label">Label</label>
        <input class="input" v-model="basketModal.label" placeholder="e.g. Bathroom Bin" />
      </div>
      <div class="mb-3">
        <label class="label">Type</label>
        <select class="input" v-model="basketModal.basket_type">
          <option value="BEDDING">Bedding</option>
          <option value="CLEANING">Cleaning</option>
          <option value="FIRST_AID_BASIC">First Aid (Basic)</option>
          <option value="FIRST_AID_ADVANCED">First Aid (Advanced)</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="label">Sub-Bin (optional, for Advanced FA)</label>
        <input class="input" v-model="basketModal.sub_bin" placeholder="e.g. TRAUMA" />
      </div>
      <div class="mb-3">
        <label class="label">NFC Tag ID (optional)</label>
        <input class="input" v-model="basketModal.nfc_tag_id" />
      </div>
      <div>
        <label class="label">Position Order</label>
        <input class="input" type="number" min="0" v-model.number="basketModal.position_order" />
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useClosetStore } from '@/stores/closets'
import { getShelves, getBaskets } from '@/api'
import AppModal from '@/components/AppModal.vue'

const store = useClosetStore()

// shelves and baskets keyed by id
const shelvesByCloset = reactive({})
const basketsByShelf = reactive({})

async function loadShelves(closetId) {
  const res = await getShelves(closetId)
  shelvesByCloset[closetId] = res.data
  for (const s of res.data) await loadBaskets(s.id)
}
async function loadBaskets(shelfId) {
  const res = await getBaskets(shelfId)
  basketsByShelf[shelfId] = res.data
}
function shelvesFor(cid) { return shelvesByCloset[cid] || [] }
function basketsFor(sid) { return basketsByShelf[sid] || [] }

onMounted(async () => {
  await store.fetchClosets()
  for (const c of store.closets) await loadShelves(c.id)
})

// --- Closet Modal ---
const closetModal = reactive({ show: false, editing: false, id: null, name: '', location: '' })
function openClosetModal(c = null) {
  closetModal.editing = !!c
  closetModal.id = c?.id ?? null
  closetModal.name = c?.name ?? ''
  closetModal.location = c?.location ?? ''
  closetModal.show = true
}
async function saveCloset() {
  if (closetModal.editing) {
    await store.editCloset(closetModal.id, { name: closetModal.name, location: closetModal.location })
  } else {
    const newC = await store.addCloset({ name: closetModal.name, location: closetModal.location })
    await loadShelves(newC.id)
  }
  closetModal.show = false
}
async function confirmDeleteCloset(c) {
  if (confirm(`Delete closet "${c.name}"? All shelves and baskets will be removed.`)) {
    await store.removeCloset(c.id)
    delete shelvesByCloset[c.id]
  }
}

// --- Shelf Modal ---
const shelfModal = reactive({ show: false, editing: false, id: null, closet_id: null, label: '', position_order: 0 })
function openShelfModal(closet, shelf = null) {
  shelfModal.editing = !!shelf
  shelfModal.id = shelf?.id ?? null
  shelfModal.closet_id = closet.id
  shelfModal.label = shelf?.label ?? ''
  shelfModal.position_order = shelf?.position_order ?? (shelvesFor(closet.id).length)
  shelfModal.show = true
}
async function saveShelf() {
  if (shelfModal.editing) {
    await store.editShelf(shelfModal.id, { label: shelfModal.label, position_order: shelfModal.position_order })
  } else {
    await store.addShelf({ closet_id: shelfModal.closet_id, label: shelfModal.label, position_order: shelfModal.position_order })
  }
  await loadShelves(shelfModal.closet_id)
  shelfModal.show = false
}
async function confirmDeleteShelf(shelf) {
  // find closet id
  let cid = null
  for (const [cKey, shelves] of Object.entries(shelvesByCloset)) {
    if (shelves.find(s => s.id === shelf.id)) { cid = cKey; break }
  }
  if (confirm(`Delete shelf "${shelf.label}"?`)) {
    await store.removeShelf(shelf.id)
    if (cid) await loadShelves(cid)
  }
}

// --- Basket Modal ---
const basketModal = reactive({ show: false, editing: false, id: null, shelf_id: null,
  label: '', basket_type: 'CLEANING', sub_bin: '', nfc_tag_id: '', position_order: 0 })
function openBasketModal(shelf, basket = null) {
  basketModal.editing = !!basket
  basketModal.id = basket?.id ?? null
  basketModal.shelf_id = shelf.id
  basketModal.label = basket?.label ?? ''
  basketModal.basket_type = basket?.basket_type ?? 'CLEANING'
  basketModal.sub_bin = basket?.sub_bin ?? ''
  basketModal.nfc_tag_id = basket?.nfc_tag_id ?? ''
  basketModal.position_order = basket?.position_order ?? (basketsFor(shelf.id).length)
  basketModal.show = true
}
async function saveBasket() {
  const data = {
    shelf_id: basketModal.shelf_id,
    label: basketModal.label,
    basket_type: basketModal.basket_type,
    sub_bin: basketModal.sub_bin || null,
    nfc_tag_id: basketModal.nfc_tag_id || null,
    position_order: basketModal.position_order,
  }
  if (basketModal.editing) {
    await store.editBasket(basketModal.id, data)
  } else {
    await store.addBasket(data)
  }
  await loadBaskets(basketModal.shelf_id)
  basketModal.show = false
}
async function confirmDeleteBasket(basket) {
  if (confirm(`Delete basket "${basket.label}"?`)) {
    await store.removeBasket(basket.id)
    await loadBaskets(basket.shelf_id)
  }
}
</script>

<style scoped>
.baskets-list { display: flex; flex-direction: column; gap: 0.4rem; }
.basket-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0.6rem;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  flex-wrap: wrap;
}
.ml-2 { margin-left: 0.5rem; }
</style>
