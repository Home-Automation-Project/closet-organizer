<template>
  <div style="max-width:600px">
    <RouterLink to="/firstaid" class="text-muted text-sm">← First Aid Hub</RouterLink>
    <h1 class="page-title mt-3">Poison Control</h1>

    <div class="card mb-4" style="background:var(--color-red-bg);border-color:var(--color-red)">
      <div style="font-size:1.5rem;font-weight:900;color:var(--color-red)">📞 1-800-222-1222</div>
      <div style="color:var(--color-text-muted);margin-top:0.4rem">U.S. Poison Control Center — available 24/7</div>
    </div>

    <div class="card mb-4">
      <div class="section-title">If someone is unconscious / not breathing</div>
      <p class="text-muted text-sm">Call 911 immediately. Begin CPR if trained. Do not induce vomiting unless instructed by Poison Control.</p>
    </div>

    <div class="card mb-4">
      <div class="section-title">What to have ready when you call</div>
      <ul class="info-list">
        <li>Person's age, weight, and symptoms</li>
        <li>Name of the product or substance (have the container)</li>
        <li>Time of exposure and amount involved</li>
        <li>How it was taken (swallowed, inhaled, skin/eye exposure)</li>
      </ul>
    </div>

    <div class="card">
      <div class="section-title">Other Emergency Numbers</div>
      <div class="contact-row"><span>Emergency / Fire / Police</span><span class="font-bold">911</span></div>
      <div class="contact-row"><span>Non-Emergency Police</span><span class="text-muted">311</span></div>
      <div class="contact-row"><span>Suicide & Crisis Lifeline</span><span class="font-bold">988</span></div>
    </div>
  </div>
</template>

<style scoped>
.info-list { list-style: disc; padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.3rem; }
.info-list li { color: var(--color-text-muted); font-size: 0.9rem; line-height: 1.4; }
.contact-row { display: flex; justify-content: space-between; padding: 0.55rem 0; border-bottom: 1px solid var(--color-border); font-size: 0.9rem; }
.contact-row:last-child { border-bottom: none; }
</style>
