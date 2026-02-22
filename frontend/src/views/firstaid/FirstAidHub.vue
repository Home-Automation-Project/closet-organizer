<template>
  <div>
    <h1 class="page-title">First Aid Hub</h1>
    <div class="hub-grid">
      <RouterLink to="/firstaid/cpr" class="hub-card">
        <div class="hub-icon">❤️</div>
        <div class="hub-label">CPR Steps</div>
        <div class="hub-desc">Step-by-step CPR guide for adults</div>
      </RouterLink>
      <RouterLink to="/firstaid/poison" class="hub-card">
        <div class="hub-icon">☠️</div>
        <div class="hub-label">Poison Control</div>
        <div class="hub-desc">Emergency numbers and guidance</div>
      </RouterLink>
      <RouterLink to="/firstaid/family" class="hub-card">
        <div class="hub-icon">👨‍👩‍👧‍👦</div>
        <div class="hub-label">Family Med Info</div>
        <div class="hub-desc">Allergies, medications, and medical history</div>
      </RouterLink>
      <RouterLink to="/firstaid/kit/basic" class="hub-card">
        <div class="hub-icon">🩹</div>
        <div class="hub-label">Basic First Aid Kit</div>
        <div class="hub-desc">Contents of the regular kit</div>
      </RouterLink>
      <RouterLink to="/firstaid/kit/advanced" class="hub-card">
        <div class="hub-icon">🚑</div>
        <div class="hub-label">Advanced First Aid Kit</div>
        <div class="hub-desc">Controlled-access trauma and medical kit</div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.hub-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.hub-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.5rem 1.25rem;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  transition: border-color 0.15s, transform 0.15s;
}
.hub-card:hover { border-color: var(--color-primary); transform: translateY(-2px); }
.hub-icon { font-size: 2rem; }
.hub-label { font-weight: 700; color: var(--color-text); font-size: 1rem; }
.hub-desc { color: var(--color-text-muted); font-size: 0.82rem; line-height: 1.4; }
</style>
