import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getWashReminders, acknowledgeWashReminder,
         getSeasonalReminders, acknowledgeSeasonalReminder } from '@/api'

export const useReminderStore = defineStore('reminders', () => {
  const washReminders = ref([])
  const seasonalReminders = ref([])

  const allActive = computed(() => [
    ...washReminders.value.map(r => ({ ...r, kind: 'wash' })),
    ...seasonalReminders.value.map(r => ({ ...r, kind: 'seasonal' })),
  ])

  async function fetchAll() {
    const [wash, seasonal] = await Promise.all([
      getWashReminders(),
      getSeasonalReminders(),
    ])
    washReminders.value = wash.data
    seasonalReminders.value = seasonal.data
  }

  async function ackWash(id) {
    await acknowledgeWashReminder(id)
    washReminders.value = washReminders.value.filter(r => r.id !== id)
  }

  async function ackSeasonal(id) {
    await acknowledgeSeasonalReminder(id)
    seasonalReminders.value = seasonalReminders.value.filter(r => r.id !== id)
  }

  return { washReminders, seasonalReminders, allActive, fetchAll, ackWash, ackSeasonal }
})
