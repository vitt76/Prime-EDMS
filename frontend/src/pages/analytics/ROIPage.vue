<template>
  <div class="container mx-auto px-4 py-6">

      <div class="mb-6">
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          :disabled="analyticsStore.isLoading"
          @click="refresh"
        >
          Обновить
        </button>
      </div>

      <ROIDashboard :data="analyticsStore.roiSummary" />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import ROIDashboard from '@/components/Analytics/ROIDashboard.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()

async function refresh(): Promise<void> {
  await analyticsStore.fetchRoiSummary()
}

onMounted(async () => {
  await refresh()
})
</script>


