<template>
  <div class="recent-assets-panel bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 p-5">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold text-neutral-900 flex items-center gap-2">
        <span class="text-xl">📷</span> Недавние активы
      </h2>
      <router-link
        :to="{ name: 'dam-gallery' }"
        class="text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        Показать все
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="homeStore.isLoading && !homeStore.recentAssets.length" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="animate-pulse">
        <div class="aspect-square bg-neutral-200 rounded-lg mb-2"></div>
        <div class="h-3 bg-neutral-200 rounded w-3/4"></div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!homeStore.recentAssets.length" class="text-center py-8 text-neutral-500">
      <p>В системе пока нет активов.</p>
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      <AssetCard
        v-for="asset in displayAssets"
        :key="asset.id"
        :asset="asset"
        :density="'compact'"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useHomeStore } from '@/stores/homeStore'
import AssetCard from '@/components/DAM/AssetCard.vue'

const homeStore = useHomeStore()

const displayAssets = computed(() => {
  return homeStore.recentAssets.slice(0, 8)
})
</script>