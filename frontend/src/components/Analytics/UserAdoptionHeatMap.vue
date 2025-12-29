<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <div>
        <h3 class="text-base font-semibold text-neutral-900">User Adoption</h3>
        <p class="text-xs text-neutral-500">MAU по department × region</p>
      </div>
    </div>

    <div v-if="departments.length === 0 || regions.length === 0" class="text-sm text-neutral-500">
      Нет данных
    </div>

    <div v-else class="overflow-auto">
      <div class="min-w-[720px]">
        <div
          class="grid gap-1"
          :style="{ gridTemplateColumns: `220px repeat(${regions.length}, minmax(72px, 1fr))` }"
        >
          <!-- Header row -->
          <div class="text-xs font-semibold text-neutral-600 py-2">Department</div>
          <div
            v-for="region in regions"
            :key="region"
            class="text-xs font-semibold text-neutral-600 py-2 text-center"
          >
            {{ region }}
          </div>

          <!-- Data rows -->
          <template v-for="dept in departments" :key="dept">
            <div class="text-xs text-neutral-700 py-2 pr-2 truncate" :title="dept">
              {{ dept }}
            </div>

            <button
              v-for="region in regions"
              :key="`${dept}-${region}`"
              type="button"
              class="h-10 rounded-md border border-neutral-200"
              :style="{ backgroundColor: cellColor(getValue(dept, region)) }"
              :title="`${dept} / ${region}: ${getValue(dept, region)} MAU`"
            >
              <span class="text-[10px] text-neutral-800">
                {{ getValue(dept, region) || '' }}
              </span>
            </button>
          </template>
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import Card from '@/components/Common/Card.vue'
import type { UserAdoptionHeatmapCell } from '@/stores/analyticsStore'

const props = defineProps<{
  heatmapData: UserAdoptionHeatmapCell[]
  departments: string[]
  regions: string[]
}>()

const valueMap = computed(() => {
  const map = new Map<string, number>()
  for (const row of props.heatmapData || []) {
    map.set(`${row.department}||${row.region}`, row.mau)
  }
  return map
})

const maxValue = computed(() => {
  let max = 0
  for (const row of props.heatmapData || []) {
    if (row.mau > max) max = row.mau
  }
  return max
})

function getValue(department: string, region: string): number {
  return valueMap.value.get(`${department}||${region}`) || 0
}

function cellColor(value: number): string {
  const max = maxValue.value
  if (!max || value <= 0) return '#ffffff'
  const ratio = Math.min(1, value / max)
  // White -> green scale
  const g = 200 + Math.round(55 * ratio)
  const r = 255 - Math.round(180 * ratio)
  const b = 255 - Math.round(200 * ratio)
  return `rgb(${r}, ${g}, ${b})`
}
</script>


