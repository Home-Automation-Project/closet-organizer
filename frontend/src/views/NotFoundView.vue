<template>
  <div class="not-found">
    <div class="code">404</div>
    <p class="message">Page not found</p>
    <RouterLink to="/" class="btn-primary">Return to Dashboard</RouterLink>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
  text-align: center;
}
.code { font-size: 6rem; font-weight: 700; color: var(--color-border); line-height: 1; }
.message { color: var(--color-muted, #6b7280); font-size: 1.25rem; }
</style>
