import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getClosets, getCloset, createCloset, updateCloset, deleteCloset,
         createShelf, updateShelf, deleteShelf,
         createBasket, updateBasket, deleteBasket } from '@/api'

export const useClosetStore = defineStore('closets', () => {
  const closets = ref([])
  const currentCloset = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchClosets() {
    loading.value = true
    error.value = null
    try {
      const res = await getClosets()
      closets.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchCloset(id) {
    loading.value = true
    error.value = null
    try {
      const res = await getCloset(id)
      currentCloset.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function addCloset(data) {
    const res = await createCloset(data)
    closets.value.push(res.data)
    return res.data
  }

  async function editCloset(id, data) {
    const res = await updateCloset(id, data)
    const idx = closets.value.findIndex(c => c.id === id)
    if (idx !== -1) closets.value[idx] = res.data
    return res.data
  }

  async function removeCloset(id) {
    await deleteCloset(id)
    closets.value = closets.value.filter(c => c.id !== id)
  }

  async function addShelf(data) {
    const res = await createShelf(data)
    return res.data
  }

  async function editShelf(id, data) {
    const res = await updateShelf(id, data)
    return res.data
  }

  async function removeShelf(id) {
    await deleteShelf(id)
  }

  async function addBasket(data) {
    const res = await createBasket(data)
    return res.data
  }

  async function editBasket(id, data) {
    const res = await updateBasket(id, data)
    return res.data
  }

  async function removeBasket(id) {
    await deleteBasket(id)
  }

  return {
    closets, currentCloset, loading, error,
    fetchClosets, fetchCloset,
    addCloset, editCloset, removeCloset,
    addShelf, editShelf, removeShelf,
    addBasket, editBasket, removeBasket,
  }
})
