<template>
  <div id="app-root">
    <AppNav />
    <ReminderBanner />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import AppNav from '@/components/AppNav.vue'
import ReminderBanner from '@/components/ReminderBanner.vue'
</script>

<style>
#app-root {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main-content {
  flex: 1;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
@media (max-width: 600px) {
  .main-content { padding: 1rem 0.75rem; }
}
</style>
