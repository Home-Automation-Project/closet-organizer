<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal">
        <div class="modal-title">{{ title }}</div>
        <slot />
        <div class="modal-footer">
          <button class="btn-ghost" @click="$emit('close')">Cancel</button>
          <button class="btn-primary" @click="$emit('confirm')">{{ confirmLabel }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: Boolean,
  title: String,
  confirmLabel: { type: String, default: 'Save' },
})
defineEmits(['close', 'confirm'])
</script>
