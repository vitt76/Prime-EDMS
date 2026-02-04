<template>
  <div
    :class="[
      'rounded-md border px-4 py-3 text-sm',
      variant === 'error' ? 'border-red-200 bg-red-50 text-red-700' : 'border-green-200 bg-green-50 text-green-700'
    ]"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'success' | 'error'
}>()
</script>
