import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getBasketInventory, upsertInventoryItem, deleteInventoryItem, scanBasket } from '@/api'

export const useInventoryStore = defineStore('inventory', () => {
  const basket = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchBasket(id) {
    loading.value = true
    error.value = null
    try {
      const res = await getBasketInventory(id)
      basket.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchByToken(token) {
    loading.value = true
    error.value = null
    try {
      const res = await scanBasket(token)
      basket.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function updateItem(basketId, itemDefId, data) {
    const res = await upsertInventoryItem(basketId, itemDefId, data)
    if (basket.value) {
      const idx = basket.value.inventory.findIndex(i => i.item_definition_id === itemDefId)
      if (idx !== -1) basket.value.inventory[idx] = res.data
      else basket.value.inventory.push(res.data)
    }
    return res.data
  }

  async function removeItem(inventoryId) {
    await deleteInventoryItem(inventoryId)
    if (basket.value) {
      basket.value.inventory = basket.value.inventory.filter(i => i.id !== inventoryId)
    }
  }

  return { basket, loading, error, fetchBasket, fetchByToken, updateItem, removeItem }
})
