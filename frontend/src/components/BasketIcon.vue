<template>
  <RouterLink :to="`/basket/${basket.id}`" class="basket-icon" :class="statusClass">
    <span class="basket-type-icon">{{ typeIcon }}</span>
    <span class="basket-label">{{ basket.label }}</span>
    <span v-if="basket.sub_bin" class="basket-sub">{{ basket.sub_bin }}</span>
    <span class="basket-status-dot" :class="statusClass"></span>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  basket: { type: Object, required: true },
})

const statusClass = computed(() => {
  const s = props.basket.status
  if (s === 'RED') return 'status-red'
  if (s === 'YELLOW') return 'status-yellow'
  return 'status-green'
})

const typeIcon = computed(() => {
  const t = props.basket.basket_type
  if (t === 'BEDDING') return '🛏️'
  if (t === 'CLEANING') return '🧹'
  if (t === 'FIRST_AID_BASIC') return '🩹'
  if (t === 'FIRST_AID_ADVANCED') return '🚑'
  return '📦'
})
</script>

<style scoped>
.basket-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 90px;
  height: 90px;
  border-radius: var(--radius);
  border: 2px solid transparent;
  background: var(--color-surface2);
  cursor: pointer;
  text-decoration: none;
  position: relative;
  transition: transform 0.15s, border-color 0.15s;
  padding: 0.5rem;
  gap: 0.2rem;
}
.basket-icon:hover { transform: scale(1.05); }

.basket-type-icon { font-size: 1.6rem; line-height: 1; }
.basket-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
  word-break: break-word;
  line-height: 1.2;
}
.basket-sub {
  font-size: 0.58rem;
  color: var(--color-text-muted);
  text-align: center;
}
.basket-status-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-green { border-color: var(--color-green); }
.status-green .basket-status-dot { background: var(--color-green); }
.status-yellow { border-color: var(--color-yellow); background: var(--color-yellow-bg); }
.status-yellow .basket-status-dot { background: var(--color-yellow); }
.status-red { border-color: var(--color-red); background: var(--color-red-bg); }
.status-red .basket-status-dot { background: var(--color-red); }
</style>
