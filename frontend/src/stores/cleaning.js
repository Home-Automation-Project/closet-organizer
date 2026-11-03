import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCleaningData, getRoom } from '@/api'

export const useCleaningStore = defineStore('cleaning', () => {
  const rooms = ref([])
  const currentRoom = ref(null)
  const completions = ref({}) // Store completions per room
  const loading = ref(false)
  const error = ref(null)

  // Load/save completions from localStorage
  function getCompletions(roomId) {
    const stored = localStorage.getItem(`cleaning_${roomId}`)
    return stored ? JSON.parse(stored) : {}
  }

  function saveCompletions(roomId, completionMap) {
    localStorage.setItem(`cleaning_${roomId}`, JSON.stringify(completionMap))
    completions.value[roomId] = completionMap
  }

  async function fetchRooms() {
    loading.value = true
    error.value = null
    try {
      const data = await getCleaningData()
      rooms.value = data.rooms || []
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch cleaning data:', e)
      rooms.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchRoom(roomId) {
    loading.value = true
    error.value = null
    try {
      currentRoom.value = await getRoom(roomId)
      // Load any saved completions
      completions.value[roomId] = getCompletions(roomId)
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch room:', e)
      currentRoom.value = null
    } finally {
      loading.value = false
    }
  }

  function toggleItem(roomId, itemKey) {
    if (!completions.value[roomId]) {
      completions.value[roomId] = {}
    }
    const isCompleted = completions.value[roomId][itemKey]
    completions.value[roomId][itemKey] = !isCompleted
    saveCompletions(roomId, completions.value[roomId])
  }

  function resetRoom(roomId) {
    completions.value[roomId] = {}
    localStorage.removeItem(`cleaning_${roomId}`)
  }

  function isItemCompleted(roomId, itemKey) {
    return completions.value[roomId]?.[itemKey] || false
  }

  return {
    rooms,
    currentRoom,
    completions,
    loading,
    error,
    fetchRooms,
    fetchRoom,
    toggleItem,
    resetRoom,
    isItemCompleted,
  }
})
