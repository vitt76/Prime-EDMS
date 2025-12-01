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
/**
 * RecentPage.vue
 * 
 * Displays assets sorted by lastAccessedAt with time-based grouping:
 * - Today
 * - Yesterday
 * - This Week
 * - Earlier
 * 
 * Backend Alignment (Mayan EDMS):
 * - documents.models.RecentDocument model
 * - Tracks document access per user
 * - mayan/apps/documents/models/recent_document_models.py
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CollectionBrowser from '@/components/collections/CollectionBrowser.vue'
import { getRecentAssetsGrouped, toggleMockFavorite, type ExtendedAsset, touchMockAsset } from '@/mocks/assets'
import { useNotificationStore } from '@/stores/notificationStore'

// ============================================================================
// STORES & ROUTER
// ============================================================================

const router = useRouter()
const notificationStore = useNotificationStore()

// ============================================================================
// STATE
// ============================================================================

const today = ref<ExtendedAsset[]>([])
const yesterday = ref<ExtendedAsset[]>([])
const thisWeek = ref<ExtendedAsset[]>([])
const earlier = ref<ExtendedAsset[]>([])
const isLoading = ref(false)

// ============================================================================
// COMPUTED
// ============================================================================

const allAssets = computed(() => [
  ...today.value,
  ...yesterday.value,
  ...thisWeek.value,
  ...earlier.value,
])

const totalCount = computed(() => allAssets.value.length)

const groupedAssets = computed(() => [
  { label: 'Сегодня', assets: today.value },
  { label: 'Вчера', assets: yesterday.value },
  { label: 'На этой неделе', assets: thisWeek.value },
  { label: 'Ранее', assets: earlier.value },
])

// ============================================================================
// DATA FETCHING
// ============================================================================

async function fetchRecent() {
  isLoading.value = true
  
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 300))
  
  try {
    const grouped = getRecentAssetsGrouped()
    today.value = grouped.today
    yesterday.value = grouped.yesterday
    thisWeek.value = grouped.thisWeek
    earlier.value = grouped.earlier
  } finally {
    isLoading.value = false
  }
}

// ============================================================================
// HANDLERS
// ============================================================================

async function handleToggleFavorite(asset: ExtendedAsset) {
  const updated = toggleMockFavorite(asset.id)
  
  if (updated) {
    // Update in all groups
    const updateInGroup = (group: ExtendedAsset[]) => {
      const index = group.findIndex(a => a.id === asset.id)
      if (index !== -1) {
        group[index] = updated
      }
    }
    
    updateInGroup(today.value)
    updateInGroup(yesterday.value)
    updateInGroup(thisWeek.value)
    updateInGroup(earlier.value)
    
    notificationStore.addNotification({
      type: 'success',
      title: updated.isFavorite ? 'Добавлено в избранное' : 'Убрано из избранного',
      message: `"${asset.label}"`,
    })
  }
}

function handleAssetClick(asset: ExtendedAsset) {
  // Touch asset to update lastAccessedAt
  touchMockAsset(asset.id)
  router.push(`/dam/assets/${asset.id}`)
}

function handlePreview(asset: ExtendedAsset) {
  touchMockAsset(asset.id)
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

