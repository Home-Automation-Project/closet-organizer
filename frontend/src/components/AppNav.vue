<template>
  <nav class="app-nav">
    <RouterLink to="/" class="nav-brand">🗄️ Closet Organizer</RouterLink>
    <div class="nav-links">
      <RouterLink to="/" :class="{ active: $route.path === '/' }">Dashboard</RouterLink>
      <RouterLink to="/setup" :class="{ active: $route.path === '/setup' }">Setup</RouterLink>
      <RouterLink to="/firstaid" :class="{ active: $route.path.startsWith('/firstaid') }">First Aid</RouterLink>
      <RouterLink to="/cleaning" :class="{ active: $route.path.startsWith('/cleaning') }">Cleaning</RouterLink>
    </div>
  </nav>
</template>

<style scoped>
.app-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 0 1.5rem;
  height: 56px;
  position: sticky;
  top: 0;
  z-index: 50;
}
.nav-brand {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
}
.nav-links {
  display: flex;
  gap: 0.25rem;
}
.nav-links a {
  color: var(--color-text-muted);
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}
.nav-links a:hover, .nav-links a.active {
  background: var(--color-surface2);
  color: var(--color-text);
}
@media (max-width: 480px) {
  .app-nav { padding: 0 0.75rem; }
  .nav-links a { padding: 0.35rem 0.6rem; font-size: 0.8rem; }
  .nav-brand { font-size: 0.9rem; }
}
</style>
