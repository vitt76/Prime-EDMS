// @ts-nocheck
<template>
  <CollectionBrowser
    title="Недавние"
    subtitle="Файлы, с которыми вы недавно работали"
    :assets="allAssets"
    :total-count="totalCount"
    :is-loading="isLoading"
    :has-more="false"
    :show-favorite-button="true"
    :show-stats="true"
    :group-by-time="true"
    :grouped-assets="groupedAssets"
    empty-title="Нет недавних файлов"
    empty-description="Откройте или просмотрите файлы, и они появятся здесь"
    empty-action-text="Перейти в галерею"
    empty-action-link="/dam"
    @toggle-favorite="handleToggleFavorite"
    @asset-click="handleAssetClick"
    @preview="handlePreview"
    @download="handleDownload"
    @share="handleShare"
  >
    <!-- Custom Empty State -->
    <template #empty-state>
      <div class="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 flex items-center justify-center mb-6">
        <svg class="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-xl font-semibold text-neutral-800 mb-2">
        История пуста
      </h3>
      <p class="text-neutral-500 mb-6">
        Откройте или просмотрите файлы в галерее,<br/>
        и они появятся в истории
      </p>
      <router-link
        to="/dam"
        class="inline-flex items-center gap-2 px-6 py-3 bg-blue-500 text-white font-medium rounded-xl
               hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
               transition-all shadow-lg shadow-blue-500/25"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Открыть галерею
      </router-link>
    </template>
  </CollectionBrowser>
</template>

<script setup lang="ts">
// @ts-nocheck
/**
 * RecentPage.vue
 *
 * Displays documents recently viewed or downloaded by the current user
 * in the current organization (Sprint 1 Discovery UX).
 * API: GET /api/v4/headless/documents/recently-viewed/ (AssetEvent-based).
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CollectionBrowser from '@/components/collections/CollectionBrowser.vue'
import { apiService } from '@/services/apiService'
import { getRecentlyViewed } from '@/services/recentlyViewedService'
import type { ExtendedAsset, Asset } from '@/types/api'
import { useNotificationStore } from '@/stores/notificationStore'

// ============================================================================
// STORES & ROUTER
// ============================================================================

const router = useRouter()
const notificationStore = useNotificationStore()

// ============================================================================
// STATE
// ============================================================================

const assets = ref<Asset[]>([])
const isLoading = ref(false)

// ============================================================================
// COMPUTED
// ============================================================================

const allAssets = computed<ExtendedAsset[]>(() =>
  assets.value.map((a) => ({ ...a, isFavorite: (a as ExtendedAsset).isFavorite ?? false }))
)

const totalCount = computed(() => assets.value.length)

const groupedAssets = computed(() => [
  { label: 'Недавно просмотренные', assets: allAssets.value },
])

// ============================================================================
// DATA FETCHING
// ============================================================================

async function fetchRecent() {
  isLoading.value = true
  try {
    const res = await getRecentlyViewed({ limit: 50, days: 30 })
    assets.value = res.results
  } finally {
    isLoading.value = false
  }
}

// ============================================================================
// HANDLERS
// ============================================================================

async function handleToggleFavorite(asset: ExtendedAsset) {
  try {
    if (asset.isFavorite) {
      await apiService.post(`/api/v4/documents/${asset.id}/remove_from_favorites/`, {})
      asset.isFavorite = false
    } else {
      await apiService.post(`/api/v4/documents/${asset.id}/add_to_favorites/`, {})
      asset.isFavorite = true
    }
    const idx = assets.value.findIndex((a) => a.id === asset.id)
    if (idx !== -1) {
      assets.value = [
        ...assets.value.slice(0, idx),
        { ...assets.value[idx], isFavorite: asset.isFavorite } as Asset,
        ...assets.value.slice(idx + 1),
      ]
    }
    notificationStore.addNotification({
      type: 'success',
      title: asset.isFavorite ? 'Добавлено в избранное' : 'Убрано из избранного',
      message: `"${asset.label}"`,
    })
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка избранного',
      message: 'Не удалось обновить избранное'
    })
    console.error(error)
  }
}

function handleAssetClick(asset: ExtendedAsset) {
  router.push(`/dam/assets/${asset.id}`)
}

function handlePreview(asset: ExtendedAsset) {
  router.push(`/dam/assets/${asset.id}`)
}

function handleDownload(asset: ExtendedAsset) {
  notificationStore.addNotification({
    type: 'info',
    title: 'Скачивание',
    message: `Начато скачивание "${asset.label}"`,
  })
}

function handleShare(asset: ExtendedAsset) {
  notificationStore.addNotification({
    type: 'info',
    title: 'Поделиться',
    message: `Функция шаринга для "${asset.label}" скоро будет доступна`,
  })
}

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  fetchRecent()
})
</script>

