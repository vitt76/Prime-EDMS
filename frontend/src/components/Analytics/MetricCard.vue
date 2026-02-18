<template>
  <div class="rounded-lg border border-neutral-200 p-4">
    <div class="text-xs text-neutral-500 mb-1">{{ label }}</div>
    <div class="text-3xl font-semibold text-neutral-900 tracking-tight">
      {{ displayValue }}
    </div>
    <div
      v-if="trend != null && trend !== 0"
      class="mt-1 text-xs"
      :class="trend > 0 ? 'text-amber-600' : 'text-emerald-600'"
    >
      {{ trend > 0 ? '↑' : '↓' }} {{ Math.abs(trend).toFixed(1) }}%
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    label: string
    value: string | number | null | undefined
    trend?: number | null
  }>(),
  { trend: null }
)

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'
  return props.value
})
</script>
