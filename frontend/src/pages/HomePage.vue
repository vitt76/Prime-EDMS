<template>
  <div class="homepage min-h-screen bg-neutral-50 dark:bg-neutral-50 pb-12">
    <!-- Header Teleport target exists in Header.vue, we don't put anything there -->

    <div class="container mx-auto px-4 py-8 max-w-7xl">
      <!-- Header / Welcome -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-neutral-900 dark:text-neutral-900 mb-2">
          Добро пожаловать, {{ userName }}!
        </h1>
        <p class="text-neutral-600 dark:text-neutral-600">
          Ваше рабочее пространство
        </p>
      </div>

      <!-- Loading / Error States -->
      <div v-if="homeStore.isLoading && !hasData" class="space-y-8">
        <!-- Skeleton for KPI Bar -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-8">
          <div v-for="i in 3" :key="i" class="bg-white rounded-lg shadow-sm p-5 animate-pulse">
            <div class="h-4 bg-neutral-200 rounded w-1/2 mb-4"></div>
            <div class="h-8 bg-neutral-200 rounded w-3/4 mb-2"></div>
            <div class="h-4 bg-neutral-200 rounded w-1/4"></div>
          </div>
        </div>
      </div>

      <div v-else-if="homeStore.error && !hasData" class="p-4 bg-error/10 border border-error rounded-lg text-error flex justify-between items-center">
        <span>{{ homeStore.error }}</span>
        <button class="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600" @click="homeStore.fetchAll()">
          Попробовать снова
        </button>
      </div>

      <template v-else>
        <!-- Top: KPI Bar -->
        <KPIBar class="mb-8" />

        <!-- 2-column Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
          <!-- Left Column (60%) -->
          <div class="lg:col-span-8 flex flex-col gap-6 lg:gap-8">
            <MyInbox />
            <RecentAssetsPanel />
            <ActivityFeedPanel />
          </div>

          <!-- Right Column (40%) -->
          <div class="lg:col-span-4 flex flex-col md:grid md:grid-cols-2 lg:flex lg:flex-col gap-6 lg:gap-8 items-start">
            <QuickActionsPanel class="w-full" />
            <AIInsightsCard class="w-full" />
            <SavedSearchesPanel class="w-full" />
            <StoragePanel class="w-full" />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useHomeStore } from '@/stores/homeStore'

import KPIBar from '@/components/HomePage/KPIBar.vue'
import MyInbox from '@/components/HomePage/MyInbox.vue'
import QuickActionsPanel from '@/components/HomePage/QuickActionsPanel.vue'
import StoragePanel from '@/components/HomePage/StoragePanel.vue'
import SavedSearchesPanel from '@/components/HomePage/SavedSearchesPanel.vue'
import RecentAssetsPanel from '@/components/HomePage/RecentAssetsPanel.vue'
import ActivityFeedPanel from '@/components/HomePage/ActivityFeedPanel.vue'
import AIInsightsCard from '@/components/HomePage/AIInsightsCard.vue'

const authStore = useAuthStore()
const homeStore = useHomeStore()

const userName = computed(() => {
  if (!authStore.user) return 'Гость'
  return authStore.user.first_name || authStore.user.username
})

const hasData = computed(() => {
  return homeStore.documentsStats !== null || homeStore.aiStats !== null
})

onMounted(() => {
  // Try to load initial data
  homeStore.fetchAll()
})
</script>