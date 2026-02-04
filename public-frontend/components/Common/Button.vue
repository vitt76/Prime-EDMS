<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="[
      'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition',
      disabled ? 'opacity-50' : '',
      variant === 'primary' ? 'bg-primary-600 text-white hover:bg-primary-500' : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
    ]"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
defineProps<{
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary'
  disabled?: boolean
}>()
</script>
