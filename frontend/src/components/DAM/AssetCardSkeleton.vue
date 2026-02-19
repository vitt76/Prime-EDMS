<template>
  <div
    class="rounded-xl border border-neutral-200 dark:border-neutral-700 overflow-hidden bg-white dark:bg-neutral-800"
    :class="density === 'comfortable' ? 'min-h-[280px]' : 'min-h-[200px]'"
  >
    <div
      class="w-full bg-neutral-200 dark:bg-neutral-700 animate-pulse"
      :class="density === 'comfortable' ? 'aspect-[4/3] min-h-[180px]' : 'aspect-video min-h-[120px]'"
    />
    <div class="p-3 space-y-2">
      <div class="h-4 bg-neutral-200 dark:bg-neutral-700 rounded animate-pulse w-3/4" />
      <div class="flex justify-between gap-2">
        <div class="h-3 bg-neutral-200 dark:bg-neutral-700 rounded animate-pulse w-16" />
        <div class="h-3 bg-neutral-200 dark:bg-neutral-700 rounded animate-pulse w-20" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    density?: 'compact' | 'comfortable'
  }>(),
  { density: 'compact' }
)
</script>
