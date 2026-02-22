<template>
  <div>
    <table v-if="items.length">
      <thead>
        <tr>
          <th>Item</th>
          <th>Category</th>
          <th>Qty</th>
          <th>Rec.</th>
          <th>Status</th>
          <th>Expires</th>
          <th v-if="editable">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td class="font-bold">{{ item.item_definition.name }}</td>
          <td class="text-muted">{{ item.item_definition.category }}</td>
          <td>
            <span v-if="!editable">{{ item.quantity }} {{ item.item_definition.unit }}</span>
            <input
              v-else
              type="number"
              min="0"
              class="input"
              style="width:70px"
              :value="item.quantity"
              @change="$emit('update-qty', item, +$event.target.value)"
            />
          </td>
          <td class="text-muted">{{ item.item_definition.recommended_qty }}</td>
          <td>
            <span class="badge" :class="qtyBadge(item.quantity_status)">{{ item.quantity_status }}</span>
          </td>
          <td>
            <span v-if="item.item_definition.has_expiration">
              <span v-if="item.expiration_date" class="badge" :class="expBadge(item.expiration_status)">
                {{ fmtDate(item.expiration_date) }}
              </span>
              <span v-else class="text-muted">—</span>
            </span>
            <span v-else class="text-muted">N/A</span>
          </td>
          <td v-if="editable">
            <button class="btn-ghost" style="font-size:0.78rem;padding:0.25rem 0.6rem"
              @click="$emit('edit-item', item)">Edit</button>
            <button class="btn-danger" style="font-size:0.78rem;padding:0.25rem 0.6rem;margin-left:0.35rem"
              @click="$emit('remove-item', item)">Remove</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="text-muted mt-3">No inventory items found.</p>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
  editable: { type: Boolean, default: false },
})
defineEmits(['update-qty', 'edit-item', 'remove-item'])

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
</script>
