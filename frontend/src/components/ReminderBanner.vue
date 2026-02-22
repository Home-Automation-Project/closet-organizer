<template>
  <div v-if="store.allActive.length" class="reminder-banner">
    <div
      v-for="reminder in store.allActive"
      :key="`${reminder.kind}-${reminder.id}`"
      class="reminder-item"
    >
      <span class="reminder-icon">{{ reminder.kind === 'wash' ? '🛏️' : '⚠️' }}</span>
      <span class="reminder-text">{{ reminderText(reminder) }}</span>
      <button class="ack-btn" @click="acknowledge(reminder)">Dismiss</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useReminderStore } from '@/stores/reminders'

const store = useReminderStore()

function reminderText(r) {
  if (r.kind === 'wash') return `Shelf ${r.shelf_id}: Wash sheets — due ${new Date(r.due_at).toLocaleDateString()}`
  return r.reminder_text
}

async function acknowledge(r) {
  if (r.kind === 'wash') await store.ackWash(r.id)
  else await store.ackSeasonal(r.id)
}

let interval
onMounted(() => {
  store.fetchAll()
  interval = setInterval(() => store.fetchAll(), 60_000)
})
onUnmounted(() => clearInterval(interval))
</script>

<style scoped>
.reminder-banner {
  background: var(--color-yellow-bg);
  border-bottom: 1px solid var(--color-yellow);
  padding: 0.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.reminder-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.875rem;
}
.reminder-text { flex: 1; color: var(--color-yellow); }
.ack-btn {
  background: transparent;
  border: 1px solid var(--color-yellow);
  color: var(--color-yellow);
  padding: 0.2rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}
.ack-btn:hover { background: var(--color-yellow); color: var(--color-bg); }
</style>
