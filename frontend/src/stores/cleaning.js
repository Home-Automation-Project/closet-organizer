import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getRoomChecklist, completeItem, uncompleteItem, resetSession } from '@/api'

export const useCleaningStore = defineStore('cleaning', () => {
  const checklist = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // session_token stored per room in localStorage
  function getSessionToken(room) {
    return localStorage.getItem(`session_${room}`) || null
  }
  function saveSessionToken(room, token) {
    localStorage.setItem(`session_${room}`, token)
  }

  async function fetchChecklist(room) {
    loading.value = true
    error.value = null
    try {
      const token = getSessionToken(room)
      const res = await getRoomChecklist(room, token)
      checklist.value = res.data
      saveSessionToken(room, res.data.session_token)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function toggleItem(room, itemKey, isCompleted) {
    const token = checklist.value?.session_token
    if (!token) return
    if (isCompleted) {
      await uncompleteItem(room, itemKey, token)
      checklist.value.completions = checklist.value.completions.filter(c => c.item_key !== itemKey)
    } else {
      const res = await completeItem(room, itemKey, token)
      checklist.value.completions.push(res.data)
    }
  }

  async function resetChecklist(room) {
    const token = checklist.value?.session_token
    if (!token) return
    await resetSession(room, token)
    if (checklist.value) checklist.value.completions = []
    localStorage.removeItem(`session_${room}`)
  }

  return { checklist, loading, error, fetchChecklist, toggleItem, resetChecklist }
})
