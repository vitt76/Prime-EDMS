<template>
  <CollectionBrowser
    title="Мои загрузки"
    subtitle="Файлы, которые вы загрузили в систему"
    :assets="assets"
    :total-count="totalCount"
    :is-loading="isLoading"
    :has-more="hasMore"
    :show-favorite-button="true"
    :show-upload-button="true"
    :show-stats="true"
    empty-title="Вы ещё не загружали файлы"
    empty-description="Загрузите первые файлы в DAM-систему"
    @toggle-favorite="handleToggleFavorite"
    @asset-click="handleAssetClick"
    @preview="handlePreview"
    @download="handleDownload"
    @share="handleShare"
    @load-more="loadMore"
    @upload="handleUpload"
  >
    <!-- Custom Empty State -->
    <template #empty-state>
      <div class="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center mb-6">
        <svg class="w-12 h-12 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>
      <h3 class="text-xl font-semibold text-neutral-800 mb-2">
        Вы ещё не загружали файлы
      </h3>
      <p class="text-neutral-500 mb-6">
        Загрузите первые файлы, чтобы начать<br/>
        работу с DAM-системой
      </p>
      <button
        type="button"
        class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-xl
               hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
               transition-all shadow-lg shadow-primary-500/25"
        @click="handleUpload"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        Загрузить файлы
      </button>
    </template>
  </CollectionBrowser>
</template>

<script setup lang="ts">
/**
 * MyUploadsPage.vue
 * 
 * Displays assets where uploadedBy.id === currentUser.id.
 * Shows a prominent "Upload New" button if the list is empty.
 * 
 * Backend Alignment (Mayan EDMS):
 * - documents.Document.owner field
 * - Or documents.DocumentFile.uploaded_by
 * - Filter by request.user in API
 */

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CollectionBrowser from '@/components/collections/CollectionBrowser.vue'
import { apiService } from '@/services/apiService'
import { assetService } from '@/services/assetService'
import type { ExtendedAsset } from '@/types/api'
import { useUIStore } from '@/stores/uiStore'
import { useNotificationStore } from '@/stores/notificationStore'

// ============================================================================
// STORES & ROUTER
// ============================================================================

const router = useRouter()
const uiStore = useUIStore()
const notificationStore = useNotificationStore()

// ============================================================================
// STATE
// ============================================================================

const assets = ref<ExtendedAsset[]>([])
const totalCount = ref(0)
const isLoading = ref(false)
const currentPage = ref(1)
const hasMore = ref(false)
const pageSize = 20

// ============================================================================
// DATA FETCHING
// ============================================================================

async function fetchMyUploads(page: number = 1, append: boolean = false) {
  isLoading.value = true

  try {
    const response = await assetService.getMyUploads({
      page,
      page_size: pageSize,
      sort: '-datetime_created'
    })

    const mapped = response.results.map(mapToExtendedAsset)

    if (append) {
      assets.value = [...assets.value, ...mapped]
    } else {
      assets.value = mapped
    }

    totalCount.value = response.count
    currentPage.value = page
    hasMore.value = Boolean(response.next)
  } catch (error: any) {
    // Gracefully handle missing headless endpoint or other API failures
    console.error('[MyUploads] Failed to load uploads', error)
    assets.value = []
    totalCount.value = 0
    hasMore.value = false
    notificationStore.addNotification({
      type: 'warning',
      title: 'Мои загрузки недоступны',
      message: error?.response?.status === 404
        ? 'Endpoint /api/v4/headless/documents/my_uploads/ недоступен. Перезапустите backend или убедитесь, что headless_api загружен.'
        : 'Не удалось загрузить список ваших файлов. Попробуйте позже.'
    })
  } finally {
    isLoading.value = false
  }
}

async function loadMore() {
  if (hasMore.value && !isLoading.value) {
    await fetchMyUploads(currentPage.value + 1, true)
  }
}

// ============================================================================
// HANDLERS
// ============================================================================

function handleUpload() {
  uiStore.openModal('upload')
}

async function handleToggleFavorite(asset: ExtendedAsset) {
  try {
    if (asset.isFavorite) {
      await apiService.post(`/api/v4/documents/${asset.id}/remove_from_favorites/`, {})
      asset.isFavorite = false
      notificationStore.addNotification({
        type: 'info',
        title: 'Убрано из избранного',
        message: `"${asset.label}" удалён из избранного`,
      })
    } else {
      await apiService.post(`/api/v4/documents/${asset.id}/add_to_favorites/`, {})
      asset.isFavorite = true
      notificationStore.addNotification({
        type: 'success',
        title: 'Добавлено в избранное',
        message: `"${asset.label}" добавлен в избранное`,
      })
    }
    // Force reactivity update
    assets.value = [...assets.value]
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка избранного',
      message: 'Не удалось обновить статус избранного',
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
  fetchMyUploads()
})

function mapToExtendedAsset(asset: any): ExtendedAsset {
  return {
    ...asset,
    isFavorite: Boolean(asset.isFavorite),
    lastAccessedAt: asset.date_added,
    sharedBy: asset.sharedBy,
    sharedAt: asset.date_added
  } as ExtendedAsset
}
</script>

