<template>
  <div class="flex items-center justify-center gap-2">
    <button class="text-sm text-neutral-600" :disabled="!previous" @click="$emit('previous')">Previous</button>
    <span class="text-sm text-neutral-500">{{ page }} / {{ totalPages }}</span>
    <button class="text-sm text-neutral-600" :disabled="!next" @click="$emit('next')">Next</button>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'previous'): void
  (e: 'next'): void
}>()

defineProps<{
  page: number
  totalPages: number
  next: string | null
  previous: string | null
}>()
</script>
