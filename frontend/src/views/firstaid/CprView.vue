<template>
  <div style="max-width:700px">
    <RouterLink to="/firstaid" class="text-muted text-sm">← First Aid Hub</RouterLink>
    <h1 class="page-title mt-3">CPR Steps</h1>
    <div v-if="!steps.length" class="spinner" />
    <div v-else class="steps-list">
      <div v-for="step in steps" :key="step.step" class="card step-card mb-3">
        <div class="step-number">Step {{ step.step }}</div>
        <div class="step-title">{{ step.title }}</div>
        <div class="step-detail">{{ step.detail }}</div>
      </div>
    </div>

    <div class="card mt-4" style="background:var(--color-red-bg);border-color:var(--color-red)">
      <div style="font-weight:700;color:var(--color-red);margin-bottom:0.5rem">⚠️ Emergency</div>
      <div style="font-size:1.1rem;font-weight:700">Call 911 immediately in any life-threatening emergency.</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCprSteps } from '@/api'

const steps = ref([])
onMounted(async () => {
  const res = await getCprSteps()
  steps.value = res.data.steps
})
</script>

<style scoped>
.step-card { display: flex; flex-direction: column; gap: 0.3rem; }
.step-number { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-primary); font-weight: 700; }
.step-title { font-size: 1.05rem; font-weight: 700; }
.step-detail { color: var(--color-text-muted); font-size: 0.9rem; line-height: 1.5; }
</style>
