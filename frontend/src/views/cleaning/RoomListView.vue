<template>
  <div>
    <h1 class="page-title">Cleaning Checklists</h1>
    <p class="text-muted text-sm mb-4">Select a room to view and check off its cleaning items. Scan the room's QR code to open it directly.</p>
    <div class="rooms-grid">
      <RouterLink
        v-for="room in rooms"
        :key="room"
        :to="`/cleaning/${room}`"
        class="room-card"
      >
        <span class="room-icon">{{ roomIcon(room) }}</span>
        <span class="room-name">{{ roomLabel(room) }}</span>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
const rooms = [
  'library', 'kitchen', 'dining_room', 'gym', 'bedroom',
  'bathroom', 'playroom', 'hallways', 'laundry_room', 'garage', 'family_room'
]

const icons = {
  library: '📚', kitchen: '🍳', dining_room: '🍽️', gym: '🏋️',
  bedroom: '🛏️', bathroom: '🚿', playroom: '🧸', hallways: '🚪',
  laundry_room: '👕', garage: '🚗', family_room: '📺',
}
const labels = {
  library: 'Library', kitchen: 'Kitchen', dining_room: 'Dining Room', gym: 'Gym',
  bedroom: 'Bedroom', bathroom: 'Bathroom', playroom: 'Playroom', hallways: 'Hallways',
  laundry_room: 'Laundry Room', garage: 'Garage', family_room: 'Family Room',
}
function roomIcon(r) { return icons[r] || '🏠' }
function roomLabel(r) { return labels[r] || r.replace(/_/g, ' ') }
</script>

<style scoped>
.rooms-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1rem; }
.room-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.25rem 1rem;
  text-align: center;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  transition: border-color 0.15s, transform 0.15s;
}
.room-card:hover { border-color: var(--color-primary); transform: translateY(-2px); }
.room-icon { font-size: 2rem; }
.room-name { font-size: 0.875rem; font-weight: 600; color: var(--color-text); }
</style>
