<template>
  <div class="dashboard-page min-h-screen bg-neutral-50 dark:bg-neutral-50">
    <div class="container mx-auto px-4 py-8">
      <!-- Welcome Banner -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-neutral-900 dark:text-neutral-900 mb-2">
          Добро пожаловать, {{ userName }}!
        </h1>
        <p class="text-neutral-600 dark:text-neutral-600">
          Обзор вашей DAM системы
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="dashboardStore.isLoading && !dashboardStore.stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div
          v-for="i in 4"
          :key="i"
          class="bg-neutral-100 dark:bg-neutral-100 rounded-lg p-6 animate-pulse"
        >
          <div class="h-4 bg-neutral-300 dark:bg-neutral-300 rounded w-1/2 mb-4"></div>
          <div class="h-8 bg-neutral-300 dark:bg-neutral-300 rounded w-3/4"></div>
        </div>
      </div>

      <!-- Error State -->
      <div
        v-else-if="dashboardStore.error && !dashboardStore.stats"
        class="mb-8 p-4 bg-error/10 border border-error rounded-lg"
      >
        <p class="text-error">{{ dashboardStore.error }}</p>
        <button
          class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors min-h-[44px]"
          @click="dashboardStore.refresh()"
          type="button"
          aria-label="Повторить загрузку"
        >
          Попробовать снова
        </button>
      </div>

      <!-- Stats Cards -->
      <div
        v-if="dashboardStore.stats"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
        role="region"
        aria-label="Статистика системы"
      >
        <!-- Total Documents -->
        <Card class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-medium text-neutral-600 dark:text-neutral-600">
              Всего документов
            </h3>
            <svg
              class="w-8 h-8 text-primary-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <p class="text-3xl font-bold text-neutral-900 dark:text-neutral-900">
            {{ dashboardStore.stats.documents.total.toLocaleString() }}
          </p>
          <p class="text-sm text-neutral-600 dark:text-neutral-600 mt-2">
            {{ dashboardStore.stats.documents.with_analysis }} с AI анализом
          </p>
        </Card>

        <!-- Completed Analyses -->
        <Card class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-medium text-neutral-600 dark:text-neutral-600">
              Завершенных анализов
            </h3>
            <svg
              class="w-8 h-8 text-success"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <p class="text-3xl font-bold text-neutral-900 dark:text-neutral-900">
            {{ dashboardStore.stats.analyses.completed.toLocaleString() }}
          </p>
          <p class="text-sm text-neutral-600 dark:text-neutral-600 mt-2">
            {{ dashboardStore.stats.analyses.processing }} в обработке
          </p>
        </Card>

        <!-- Pending Analyses -->
        <Card class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-medium text-neutral-600 dark:text-neutral-600">
              Ожидающих анализа
            </h3>
            <svg
              class="w-8 h-8 text-warning"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <p class="text-3xl font-bold text-neutral-900 dark:text-neutral-900">
            {{ dashboardStore.stats.analyses.pending.toLocaleString() }}
          </p>
          <p class="text-sm text-neutral-600 dark:text-neutral-600 mt-2">
            {{ dashboardStore.stats.analyses.failed }} ошибок
          </p>
        </Card>

        <!-- Storage Usage -->
        <Card class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-medium text-neutral-600 dark:text-neutral-600">
              Использовано хранилища
            </h3>
            <svg
              class="w-8 h-8 text-primary-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
              />
            </svg>
          </div>
          <p class="text-3xl font-bold text-neutral-900 dark:text-neutral-900">
            {{ dashboardStore.formattedStorageUsed }}
          </p>
          <p class="text-sm text-neutral-600 dark:text-neutral-600 mt-2">
            из {{ dashboardStore.formattedStorageTotal }}
            ({{ dashboardStore.storageUsagePercentage }}%)
          </p>
        </Card>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column: Recent Assets & Activity Feed -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Recent Assets -->
          <Card class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900">
                Недавние активы
              </h2>
              <router-link
                to="/dam/gallery"
                class="text-sm text-primary-500 hover:text-primary-600 transition-colors min-h-[44px] flex items-center"
                aria-label="Перейти к галерее активов"
              >
                Смотреть все →
              </router-link>
            </div>
            <div v-if="recentAssets.length === 0" class="text-center py-8">
              <p class="text-neutral-600 dark:text-neutral-600">
                Нет недавних активов
              </p>
            </div>
            <div
              v-else
              class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4"
              role="grid"
              aria-label="Недавние активы"
            >
              <div
                v-for="asset in recentAssets"
                :key="asset.id"
                class="cursor-pointer"
                @click="goToAsset(asset.id)"
                @keydown.enter="goToAsset(asset.id)"
                role="gridcell"
                tabindex="0"
                :aria-label="`Актив: ${asset.label}`"
              >
                <div class="relative aspect-square bg-neutral-100 dark:bg-neutral-100 rounded-lg overflow-hidden mb-2">
                  <img
                    v-if="asset.thumbnail_url"
                    :src="asset.thumbnail_url"
                    :alt="asset.label"
                    class="w-full h-full object-cover"
                    loading="lazy"
                  />
                  <div
                    v-else
                    class="w-full h-full flex items-center justify-center"
                  >
                    <svg
                      class="w-12 h-12 text-neutral-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                </div>
                <p class="text-sm font-medium text-neutral-900 dark:text-neutral-900 truncate">
                  {{ asset.label }}
                </p>
                <p class="text-xs text-neutral-600 dark:text-neutral-600">
                  {{ formatDate(asset.date_added) }}
                </p>
              </div>
            </div>
          </Card>

          <!-- Activity Feed -->
          <Card class="p-6">
            <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
              Активность
            </h2>
            <div v-if="dashboardStore.activityFeed.length === 0" class="text-center py-8">
              <p class="text-neutral-600 dark:text-neutral-600">
                Нет недавней активности
              </p>
            </div>
            <div
              v-else
              class="space-y-4"
              role="list"
              aria-label="Лента активности"
            >
              <div
                v-for="activity in dashboardStore.activityFeed"
                :key="activity.id"
                class="flex items-start gap-4 p-3 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-100 transition-colors"
                role="listitem"
              >
                <div class="flex-shrink-0 w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-100 flex items-center justify-center">
                  <svg
                    class="w-5 h-5 text-primary-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      :d="getActivityIcon(activity.type)"
                    />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-neutral-900 dark:text-neutral-900">
                    <span class="font-medium">{{ activity.user }}</span>
                    {{ activity.description }}
                    <span
                      v-if="activity.asset_label"
                      class="font-medium"
                    >
                      {{ activity.asset_label }}
                    </span>
                  </p>
                  <p class="text-xs text-neutral-600 dark:text-neutral-600 mt-1">
                    {{ formatRelativeTime(activity.timestamp) }}
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <!-- Right Column: Storage Metrics & Quick Actions -->
        <div class="space-y-6">
          <!-- Storage Metrics -->
          <Card class="p-6" v-if="dashboardStore.storageMetrics">
            <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
              Хранилище
            </h2>
            <div class="mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm text-neutral-600 dark:text-neutral-600">
                  Использовано
                </span>
                <span class="text-sm font-medium text-neutral-900 dark:text-neutral-900">
                  {{ dashboardStore.storageUsagePercentage }}%
                </span>
              </div>
              <div class="w-full bg-neutral-200 dark:bg-neutral-200 rounded-full h-2">
                <div
                  class="bg-primary-500 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${dashboardStore.storageUsagePercentage}%` }"
                  role="progressbar"
                  :aria-valuenow="dashboardStore.storageUsagePercentage"
                  aria-valuemin="0"
                  aria-valuemax="100"
                  :aria-label="`Использовано ${dashboardStore.storageUsagePercentage}% хранилища`"
                ></div>
              </div>
              <div class="mt-4 space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-neutral-600 dark:text-neutral-600">Использовано:</span>
                  <span class="font-medium text-neutral-900 dark:text-neutral-900">
                    {{ dashboardStore.formattedStorageUsed }}
                  </span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-neutral-600 dark:text-neutral-600">Всего:</span>
                  <span class="font-medium text-neutral-900 dark:text-neutral-900">
                    {{ dashboardStore.formattedStorageTotal }}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          <!-- Quick Actions -->
          <Card class="p-6">
            <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
              Быстрые действия
            </h2>
            <div class="space-y-2">
              <router-link
                to="/dam/gallery"
                class="block w-full px-4 py-3 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors text-center font-medium min-h-[44px] flex items-center justify-center"
                aria-label="Перейти к галерее активов"
              >
                Просмотреть активы
              </router-link>
              <button
                class="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-100 text-neutral-900 dark:text-neutral-900 rounded-md hover:bg-neutral-200 dark:hover:bg-neutral-200 transition-colors font-medium min-h-[44px]"
                @click="handleUpload"
                type="button"
                aria-label="Загрузить новый актив"
              >
                Загрузить актив
              </button>
              <router-link
                to="/distribution"
                class="block w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-100 text-neutral-900 dark:text-neutral-900 rounded-md hover:bg-neutral-200 dark:hover:bg-neutral-200 transition-colors text-center font-medium min-h-[44px] flex items-center justify-center"
                aria-label="Перейти к публикациям"
              >
                Управление публикациями
              </router-link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboardStore'
import { useAssetStore } from '@/stores/assetStore'
import { useAuthStore } from '@/stores/authStore'
import Card from '@/components/Common/Card.vue'
import type { Asset } from '@/types/api'
import { formatDate, formatRelativeTime } from '@/utils/formatters'

const router = useRouter()
const dashboardStore = useDashboardStore()
const assetStore = useAssetStore()
const authStore = useAuthStore()

const userName = computed(() => {
  return authStore.user?.first_name || authStore.user?.username || 'Пользователь'
})

const recentAssets = computed<Asset[]>(() => {
  // Get recent assets from assetStore (first 8)
  return assetStore.assets.slice(0, 8)
})

function goToAsset(assetId: number) {
  router.push(`/dam/assets/${assetId}`)
}

function handleUpload() {
  // Emit event to open upload modal (handled by parent layout)
  // For now, navigate to gallery
  router.push('/dam/gallery')
}

// formatRelativeTime is imported from utils/formatters

function getActivityIcon(type: string): string {
  const icons: Record<string, string> = {
    upload: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12',
    download: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4',
    share: 'M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.552 3.546a2 2 0 002.938-2.187l.546-2.59A4.998 4.998 0 0017 12c0-.482-.114-.938-.316-1.342m0 2.684L12.448 8.454a2 2 0 00-2.938-2.187l-.546 2.59A4.998 4.998 0 007 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684',
    comment: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
    tag: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z',
    delete: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16'
  }
  return icons[type] || icons.upload
}

onMounted(async () => {
  // Load dashboard data
  await dashboardStore.refresh()
  
  // Load recent assets if not loaded
  if (assetStore.assets.length === 0) {
    await assetStore.fetchAssets({ page_size: 8 })
  }
})
</script>

<style scoped>
.dashboard-page {
  padding-top: calc(var(--header-height, 64px) + 1rem);
}
</style>

