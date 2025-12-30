<template>
  <svg :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`" aria-label="sparkline">
    <polyline
      v-if="points"
      fill="none"
      stroke="#10b981"
      stroke-width="2"
      :points="points"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  values: number[]
}>()

const width = 88
const height = 24
const padding = 2

const points = computed(() => {
  const values = props.values || []
  if (!values.length) return ''
  const max = Math.max(...values, 1)
  const min = Math.min(...values, 0)
  const span = Math.max(1, max - min)

  return values
    .map((v, i) => {
      const x = padding + (i * (width - padding * 2)) / Math.max(1, values.length - 1)
      const y = height - padding - ((v - min) * (height - padding * 2)) / span
      return `${x},${y}`
    })
    .join(' ')
})
</script>


