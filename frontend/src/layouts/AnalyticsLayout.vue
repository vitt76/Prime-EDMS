<template>
  <div class="min-h-screen bg-neutral-50">
    <AnalyticsNavigation />
    <div
      v-if="bannerVisible"
      class="bg-white border-b border-neutral-200"
    >
      <div class="container mx-auto px-4 py-3">
        <div class="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2">
          <svg class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86l-7.4 13.03A2 2 0 004.63 20h14.74a2 2 0 001.74-3.11l-7.4-13.03a2 2 0 00-3.42 0z" />
          </svg>
          <div class="flex-1">
            <div class="text-sm font-semibold text-amber-900">Проблема загрузки данных аналитики</div>
            <div class="text-sm text-amber-900/80 mt-0.5">
              {{ analyticsStore.error }}
            </div>
          </div>
          <button
            class="px-2 py-1 text-sm rounded-md border border-amber-300 text-amber-900 hover:bg-amber-100"
            type="button"
            @click="dismissed = true"
          >
            Скрыть
          </button>
        </div>
      </div>
    </div>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import AnalyticsNavigation from '@/components/Analytics/AnalyticsNavigation.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()
const dismissed = ref(false)

watch(
  () => analyticsStore.error,
  () => {
    dismissed.value = false
  }
)

const bannerVisible = computed(() => {
  return !!analyticsStore.error && dismissed.value === false
})
</script>


