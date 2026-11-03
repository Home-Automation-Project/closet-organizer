import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getBasketInventory, updateInventoryItem, deleteInventoryItem } from '@/api'

export const useInventoryStore = defineStore('inventory', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)
  const currentBasketId = ref(null)

  async function fetchBasket(basketId) {
    loading.value = true
    error.value = null
    currentBasketId.value = basketId
    try {
      items.value = await getBasketInventory(basketId)
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch inventory:', e)
      items.value = []
    } finally {
      loading.value = false
    }
  }

  async function updateItem(basketId, itemName, quantity, expirationDate = null, notes = '') {
    try {
      await updateInventoryItem(basketId, itemName, quantity, expirationDate, notes)
      // Refresh the list
      await fetchBasket(basketId)
    } catch (e) {
      error.value = e.message
      console.error('Failed to update inventory:', e)
      throw e
    }
  }

  async function removeItem(basketId, itemName) {
    try {
      await deleteInventoryItem(basketId, itemName)
      // Refresh the list
      await fetchBasket(basketId)
    } catch (e) {
      error.value = e.message
      console.error('Failed to delete inventory:', e)
      throw e
    }
  }

  return { items, loading, error, currentBasketId, fetchBasket, updateItem, removeItem }
})
