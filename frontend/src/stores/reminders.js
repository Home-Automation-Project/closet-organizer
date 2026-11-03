import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getReminders, acknowledgeReminder } from '@/api'

export const useReminderStore = defineStore('reminders', () => {
  const reminders = ref([])
  const loading = ref(false)
  const error = ref(null)

  const allActive = computed(() => {
    return reminders.value.filter(r => !r.acknowledged)
  })

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      reminders.value = await getReminders()
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch reminders:', e)
    } finally {
      loading.value = false
    }
  }

  async function acknowledge(id) {
    try {
      await acknowledgeReminder(id)
      // Remove from list
      reminders.value = reminders.value.filter(r => r.id !== id)
    } catch (e) {
      error.value = e.message
      console.error('Failed to acknowledge reminder:', e)
    }
  }

  return { reminders, loading, error, allActive, fetchAll, acknowledge }
})
