<template>
  <svg
    :width="width"
    :height="height"
    :viewBox="`0 0 ${width} ${height}`"
    aria-label="trend sparkline"
  >
    <polyline
      v-if="points"
      fill="none"
      :stroke="color"
      :stroke-width="strokeWidth"
      :points="points"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  values: number[]
  width?: number
  height?: number
  color?: string
  strokeWidth?: number
}>()

const width = computed(() => props.width ?? 88)
const height = computed(() => props.height ?? 24)
const padding = 2
const color = computed(() => props.color ?? '#10b981')
const strokeWidth = computed(() => props.strokeWidth ?? 2)

const points = computed(() => {
  const values = props.values || []
  if (!values.length) return ''

  const max = Math.max(...values, 1)
  const min = Math.min(...values, 0)
  const span = Math.max(1, max - min)

  return values
    .map((v, i) => {
      const x = padding + (i * (width.value - padding * 2)) / Math.max(1, values.length - 1)
      const y = height.value - padding - ((v - min) * (height.value - padding * 2)) / span
      return `${x},${y}`
    })
    .join(' ')
})
</script>


