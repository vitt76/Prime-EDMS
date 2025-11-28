<template>
  <CollectionBrowser
    title="Избранное"
    subtitle="Файлы, которые вы добавили в избранное"
    :assets="assets"
    :total-count="totalCount"
    :is-loading="isLoading"
    :has-more="hasMore"
    :show-favorite-button="true"
    :show-stats="true"
    empty-title="Нет избранных файлов"
    empty-description="Добавляйте файлы в избранное, нажав на сердечко ❤️ на карточке актива"
    empty-action-text="Перейти в галерею"
    empty-action-link="/dam"
    @toggle-favorite="handleToggleFavorite"
    @asset-click="handleAssetClick"
    @preview="handlePreview"
    @download="handleDownload"
    @share="handleShare"
    @load-more="loadMore"
  >
    <!-- Custom Empty State -->
    <template #empty-state>
      <div class="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-error-100 to-error-50 flex items-center justify-center mb-6">
        <svg class="w-12 h-12 text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </div>
      <h3 class="text-xl font-semibold text-neutral-800 mb-2">
        Нет избранных файлов
      </h3>
      <p class="text-neutral-500 mb-6">
        Добавляйте файлы в избранное, нажав на сердечко<br/>
        на карточке актива в галерее
      </p>
      <router-link
        to="/dam"
        class="inline-flex items-center gap-2 px-6 py-3 bg-error-500 text-white font-medium rounded-xl
               hover:bg-error-600 focus:ring-2 focus:ring-error-500 focus:ring-offset-2
               transition-all shadow-lg shadow-error-500/25"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Перейти в галерею
      </router-link>
    </template>
  </CollectionBrowser>
</template>

<script setup lang="ts">
/**
 * FavoritesPage.vue
 * 
 * Displays assets where isFavorite === true.
 * Users can un-favorite items directly from this page.
 * 
 * Backend Alignment (Mayan EDMS):
 * - Would use a separate "bookmarks" or "favorites" table
 * - Or leverage tags with special "favorite" tag
 * - ACL permissions for viewing favorites
 */

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CollectionBrowser from '@/components/collections/CollectionBrowser.vue'
import { getMockFavorites, toggleMockFavorite, type ExtendedAsset } from '@/mocks/assets'
import { useNotificationStore } from '@/stores/notificationStore'

// ============================================================================
// STORES & ROUTER
// ============================================================================

const router = useRouter()
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

async function fetchFavorites(page: number = 1, append: boolean = false) {
  isLoading.value = true
  
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 300))
  
  try {
    const response = getMockFavorites(page, pageSize)
    
    if (append) {
      assets.value = [...assets.value, ...response.results]
    } else {
      assets.value = response.results
    }
    
    totalCount.value = response.count
    currentPage.value = page
    hasMore.value = !!response.next
  } finally {
    isLoading.value = false
  }
}

async function loadMore() {
  if (hasMore.value && !isLoading.value) {
    await fetchFavorites(currentPage.value + 1, true)
  }
}

// ============================================================================
// HANDLERS
// ============================================================================

async function handleToggleFavorite(asset: ExtendedAsset) {
  const updated = toggleMockFavorite(asset.id)
  
  if (updated) {
    // If un-favorited, remove from list immediately (UX enhancement)
    if (!updated.isFavorite) {
      assets.value = assets.value.filter(a => a.id !== asset.id)
      totalCount.value--
      
      notificationStore.addNotification({
        type: 'info',
        title: 'Убрано из избранного',
        message: `"${asset.label}" удалён из избранного`,
      })
    }
  }
}

function handleAssetClick(asset: ExtendedAsset) {
  router.push(`/dam/assets/${asset.id}`)
}

function handlePreview(asset: ExtendedAsset) {
  // Open preview modal or navigate to asset detail
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
  fetchFavorites()
})
</script>

