import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getClosets, getCloset } from '@/api'

export const useClosetStore = defineStore('closets', () => {
  const closets = ref([])
  const currentCloset = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchClosets() {
    loading.value = true
    error.value = null
    try {
      closets.value = await getClosets()
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch closets:', e)
      closets.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchCloset(closetId) {
    loading.value = true
    error.value = null
    try {
      currentCloset.value = await getCloset(closetId)
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch closet:', e)
      currentCloset.value = null
    } finally {
      loading.value = false
    }
  }

  return {
    closets,
    currentCloset,
    loading,
    error,
    fetchClosets,
    fetchCloset,
  }
})
