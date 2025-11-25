<template>
  <div class="asset-detail-page">
    <!-- Loading State -->
    <div v-if="assetStore.isLoading && !assetStore.currentAsset" class="p-8 text-center">
      <div class="animate-spin h-8 w-8 mx-auto text-primary-500"></div>
      <p class="mt-4 text-neutral-600 dark:text-neutral-600">Загрузка...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="assetStore.error && !assetStore.currentAsset" class="p-8 text-center">
      <div class="max-w-md mx-auto">
        <svg
          class="mx-auto h-12 w-12 text-error"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-neutral-900 dark:text-neutral-900">
          Ошибка загрузки
        </h3>
        <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-600">
          {{ assetStore.error }}
        </p>
        <button
          class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
          @click="handleRetry"
        >
          Попробовать снова
        </button>
      </div>
    </div>

    <!-- Asset Detail Content -->
    <div v-else-if="assetStore.currentAsset" class="asset-detail-content">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Preview Pane (Left 60% on desktop) -->
        <div class="lg:col-span-2">
          <div class="bg-neutral-50 dark:bg-neutral-50 rounded-lg p-4">
            <!-- Image/Video Preview -->
            <div class="relative w-full bg-neutral-100 dark:bg-neutral-100 rounded-lg overflow-hidden" style="aspect-ratio: 16/9; min-height: 400px;">
              <img
                v-if="isImage"
                :src="previewUrl"
                :alt="assetStore.currentAsset.label"
                class="w-full h-full object-contain"
                @error="handleImageError"
              />
              <video
                v-else-if="isVideo"
                :src="previewUrl"
                controls
                class="w-full h-full object-contain"
              >
                Ваш браузер не поддерживает видео.
              </video>
              <div
                v-else
                class="w-full h-full flex items-center justify-center"
              >
                <div class="text-center">
                  <svg
                    class="mx-auto h-16 w-16 text-neutral-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                  <p class="mt-4 text-neutral-600 dark:text-neutral-600">
                    Предпросмотр недоступен для этого типа файла
                  </p>
                  <button
                    class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
                    @click="handleDownload"
                  >
                    Скачать файл
                  </button>
                </div>
              </div>

              <!-- Zoom Controls (for images) -->
              <div
                v-if="isImage"
                class="absolute bottom-4 right-4 flex gap-2"
              >
                <button
                  class="p-2 bg-white dark:bg-neutral-800 rounded-md shadow-md hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                  @click="zoomOut"
                  aria-label="Уменьшить"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"
                    />
                  </svg>
                </button>
                <button
                  class="p-2 bg-white dark:bg-neutral-800 rounded-md shadow-md hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                  @click="zoomIn"
                  aria-label="Увеличить"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"
                    />
                  </svg>
                </button>
                <button
                  class="p-2 bg-white dark:bg-neutral-800 rounded-md shadow-md hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                  @click="resetZoom"
                  aria-label="Сбросить масштаб"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                </button>
              </div>

              <!-- Navigation Arrows (if related assets available) -->
              <div
                v-if="relatedAssets.length > 0"
                class="absolute top-1/2 left-4 transform -translate-y-1/2"
              >
                <button
                  v-if="previousAsset"
                  class="p-2 bg-white dark:bg-neutral-800 rounded-full shadow-md hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                  @click="navigateToAsset(previousAsset.id)"
                  aria-label="Предыдущий актив"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                </button>
              </div>
              <div
                v-if="relatedAssets.length > 0"
                class="absolute top-1/2 right-4 transform -translate-y-1/2"
              >
                <button
                  v-if="nextAsset"
                  class="p-2 bg-white dark:bg-neutral-800 rounded-full shadow-md hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                  @click="navigateToAsset(nextAsset.id)"
                  aria-label="Следующий актив"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Asset Title -->
            <div class="mt-4">
              <h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-900">
                {{ assetStore.currentAsset.label }}
              </h1>
              <p v-if="assetStore.currentAsset.tags && assetStore.currentAsset.tags.length > 0" class="mt-2 flex flex-wrap gap-2">
                <Badge
                  v-for="tag in assetStore.currentAsset.tags"
                  :key="tag"
                  variant="info"
                  size="sm"
                >
                  {{ tag }}
                </Badge>
              </p>
            </div>
          </div>
        </div>

        <!-- Metadata Panel (Right 40% on desktop) -->
        <div class="lg:col-span-1">
          <div class="bg-neutral-0 dark:bg-neutral-0 border border-neutral-300 dark:border-neutral-300 rounded-lg sticky top-4 max-h-[calc(100vh-8rem)] overflow-y-auto">
            <MetadataPanel
              :asset="assetStore.currentAsset"
              @download="handleDownload"
              @share="handleShare"
              @version-select="handleVersionSelect"
              @comment-added="handleCommentAdded"
              @comment-updated="handleCommentUpdated"
              @comment-deleted="handleCommentDeleted"
              @version-download="handleVersionDownload"
              @version-restore="handleVersionRestore"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assetStore'
import MetadataPanel from '@/components/DAM/MetadataPanel.vue'
import Badge from '@/components/Common/Badge.vue'
import type { Asset, Comment, Version } from '@/types/api'

const route = useRoute()
const router = useRouter()
const assetStore = useAssetStore()

const zoomLevel = ref(1)
const imageError = ref(false)

// Get preview URL
const previewUrl = computed(() => {
  const asset = assetStore.currentAsset
  if (!asset) return ''
  return asset.preview_url || asset.thumbnail_url || ''
})

// Check file type
const isImage = computed(() => {
  const asset = assetStore.currentAsset
  if (!asset) return false
  return asset.mime_type?.startsWith('image/') || false
})

const isVideo = computed(() => {
  const asset = assetStore.currentAsset
  if (!asset) return false
  return asset.mime_type?.startsWith('video/') || false
})

// Related assets (placeholder - would come from API)
const relatedAssets = computed<Asset[]>(() => {
  // In real implementation, this would fetch related assets from API
  return []
})

const currentAssetIndex = computed(() => {
  if (!assetStore.currentAsset) return -1
  return relatedAssets.value.findIndex((a) => a.id === assetStore.currentAsset?.id)
})

const previousAsset = computed(() => {
  const index = currentAssetIndex.value
  if (index > 0) {
    return relatedAssets.value[index - 1]
  }
  return null
})

const nextAsset = computed(() => {
  const index = currentAssetIndex.value
  if (index >= 0 && index < relatedAssets.value.length - 1) {
    return relatedAssets.value[index + 1]
  }
  return null
})

onMounted(async () => {
  const assetId = parseInt(route.params.id as string, 10)
  if (assetId && (!assetStore.currentAsset || assetStore.currentAsset.id !== assetId)) {
    await assetStore.getAssetDetail(assetId)
  }

  // Keyboard navigation
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})

function handleRetry() {
  const assetId = parseInt(route.params.id as string, 10)
  if (assetId) {
    assetStore.getAssetDetail(assetId)
  }
}

function handleDownload() {
  const asset = assetStore.currentAsset
  if (!asset) return

  // In real implementation, this would trigger download via API
  const downloadUrl = asset.preview_url || asset.thumbnail_url
  if (downloadUrl) {
    window.open(downloadUrl, '_blank')
  }
}

function handleShare() {
  // TODO: Open share modal
  console.log('Share asset:', assetStore.currentAsset?.id)
}

function handleVersionSelect(versionId: number) {
  // TODO: Load specific version
  console.log('Select version:', versionId)
}

function handleCommentAdded(comment: Comment) {
  // Refresh asset detail to get updated comments
  const assetId = parseInt(route.params.id as string, 10)
  if (assetId) {
    assetStore.getAssetDetail(assetId)
  }
}

function handleCommentUpdated(comment: Comment) {
  // Refresh asset detail to get updated comments
  const assetId = parseInt(route.params.id as string, 10)
  if (assetId) {
    assetStore.getAssetDetail(assetId)
  }
}

function handleCommentDeleted(commentId: number) {
  // Refresh asset detail to get updated comments
  const assetId = parseInt(route.params.id as string, 10)
  if (assetId) {
    assetStore.getAssetDetail(assetId)
  }
}

function handleVersionDownload(version: Version) {
  // Version download is handled in VersionHistory component
  console.log('Download version:', version.id)
}

function handleVersionRestore(version: Version) {
  // Refresh asset detail after restore
  const assetId = parseInt(route.params.id as string, 10)
  if (assetId) {
    assetStore.getAssetDetail(assetId)
  }
}

function handleImageError() {
  imageError.value = true
}

function zoomIn() {
  zoomLevel.value = Math.min(zoomLevel.value + 0.25, 3)
}

function zoomOut() {
  zoomLevel.value = Math.max(zoomLevel.value - 0.25, 0.5)
}

function resetZoom() {
  zoomLevel.value = 1
}

function navigateToAsset(assetId: number) {
  router.push(`/dam/assets/${assetId}`)
}

function handleKeyDown(event: KeyboardEvent) {
  // Arrow keys for navigation
  if (event.key === 'ArrowLeft' && previousAsset.value) {
    navigateToAsset(previousAsset.value.id)
  } else if (event.key === 'ArrowRight' && nextAsset.value) {
    navigateToAsset(nextAsset.value.id)
  }
}
</script>


<style scoped>
.asset-detail-page {
  width: 100%;
  min-height: calc(100vh - 4rem);
  padding: 1.5rem;
}

.asset-detail-content {
  max-width: 1400px;
  margin: 0 auto;
}

@media (max-width: 1024px) {
  .asset-detail-content {
    padding: 1rem;
  }
}
</style>
