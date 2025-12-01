<template>
  <CollectionBrowser
    title="Доступные мне"
    subtitle="Файлы, которыми с вами поделились коллеги"
    :assets="assets"
    :total-count="totalCount"
    :is-loading="isLoading"
    :has-more="hasMore"
    :show-favorite-button="true"
    :show-owner="true"
    :show-stats="true"
    empty-title="Нет расшаренных файлов"
    empty-description="Когда коллеги поделятся с вами файлами, они появятся здесь"
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
      <div class="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-purple-100 to-purple-50 flex items-center justify-center mb-6">
        <svg class="w-12 h-12 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <h3 class="text-xl font-semibold text-neutral-800 mb-2">
        Нет расшаренных файлов
      </h3>
      <p class="text-neutral-500 mb-6">
        Когда коллеги поделятся с вами файлами,<br/>
        они появятся здесь
      </p>
      
      <!-- Users who might share -->
      <div class="flex items-center justify-center gap-2 mb-6">
        <span class="text-xs text-neutral-400">Ваши коллеги:</span>
        <div class="flex -space-x-2">
          <img
            v-for="(user, i) in mockUsers.slice(0, 4)"
            :key="i"
            :src="user.avatar_url"
            :alt="user.first_name"
            class="w-8 h-8 rounded-full border-2 border-white"
          />
          <div class="w-8 h-8 rounded-full bg-neutral-200 border-2 border-white flex items-center justify-center text-xs font-medium text-neutral-600">
            +{{ mockUsers.length - 4 }}
          </div>
        </div>
      </div>
      
      <router-link
        to="/dam"
        class="inline-flex items-center gap-2 px-6 py-3 bg-purple-500 text-white font-medium rounded-xl
               hover:bg-purple-600 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2
               transition-all shadow-lg shadow-purple-500/25"
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
 * SharedWithMePage.vue
 * 
 * Displays assets owned by others but visible to current user.
 * Shows a small avatar of the owner on the card.
 * 
 * Backend Alignment (Mayan EDMS):
 * - acls.AccessControlList model
 * - Documents where user has view permission via ACL
 * - But document.owner != current_user
 * - Filter: AccessControlList.objects.restrict_queryset(permission, queryset, user)
 */

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CollectionBrowser from '@/components/collections/CollectionBrowser.vue'
import { getMockSharedWithMe, toggleMockFavorite, OTHER_USERS, type ExtendedAsset } from '@/mocks/assets'
import { useNotificationStore } from '@/stores/notificationStore'

// ============================================================================
// STORES & ROUTER
// ============================================================================

const router = useRouter()
const notificationStore = useNotificationStore()

// Mock users for empty state display
const mockUsers = OTHER_USERS

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

async function fetchSharedWithMe(page: number = 1, append: boolean = false) {
  isLoading.value = true
  
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 300))
  
  try {
    const response = getMockSharedWithMe(page, pageSize)
    
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
    await fetchSharedWithMe(currentPage.value + 1, true)
  }
}

// ============================================================================
// HANDLERS
// ============================================================================

async function handleToggleFavorite(asset: ExtendedAsset) {
  const updated = toggleMockFavorite(asset.id)
  
  if (updated) {
    // Update in local list
    const index = assets.value.findIndex(a => a.id === asset.id)
    if (index !== -1) {
      assets.value[index] = updated
    }
    
    notificationStore.addNotification({
      type: 'success',
      title: updated.isFavorite ? 'Добавлено в избранное' : 'Убрано из избранного',
      message: `"${asset.label}"`,
    })
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
  fetchSharedWithMe()
})
</script>

