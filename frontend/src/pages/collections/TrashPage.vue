<template>
  <div class="collection-browser min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-neutral-900">Корзина</h1>
          <p class="mt-1 text-sm text-neutral-600">Документы, перемещенные в корзину</p>
        </div>
        
        <!-- Header Actions -->
        <div class="flex items-center gap-3">
          <button
            v-if="selectedDocuments.length > 0"
            type="button"
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white text-sm font-semibold rounded-xl hover:bg-primary-700 transition-colors"
            @click="handleRestoreSelected"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Восстановить ({{ selectedDocuments.length }})
          </button>
          <button
            v-if="selectedDocuments.length > 0"
            type="button"
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-red-600 text-white text-sm font-semibold rounded-xl hover:bg-red-700 transition-colors"
            @click="handleDeleteSelected"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Удалить ({{ selectedDocuments.length }})
          </button>
          <button
            v-if="documents.length > 0"
            type="button"
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-red-600 text-white text-sm font-semibold rounded-xl hover:bg-red-700 transition-colors"
            @click="handleEmptyTrash"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Очистить корзину
          </button>
        </div>
      </div>
      
      <!-- Stats Bar -->
      <div v-if="!isLoading && documents.length > 0" class="mb-6">
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-xl border border-neutral-200 text-sm text-neutral-600">
          <span class="font-medium text-neutral-900">{{ totalCount }}</span>
          <span>{{ pluralize(totalCount, 'документ', 'документа', 'документов') }}</span>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="isLoading && documents.length === 0" class="py-12">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          <div
            v-for="i in 10"
            :key="i"
            class="bg-white rounded-xl border border-neutral-200 overflow-hidden animate-pulse"
          >
            <div class="aspect-video bg-neutral-200" />
            <div class="p-3 space-y-2">
              <div class="h-4 bg-neutral-200 rounded w-3/4" />
              <div class="flex justify-between">
                <div class="h-3 bg-neutral-200 rounded w-16" />
                <div class="h-3 bg-neutral-200 rounded w-20" />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div
        v-else-if="documents.length === 0 && !isLoading"
        class="flex items-center justify-center min-h-[60vh] p-8"
      >
        <div class="max-w-md text-center">
          <div class="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-neutral-100 to-neutral-50 flex items-center justify-center mb-6">
            <svg class="w-12 h-12 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-neutral-800 mb-2">
            Корзина пуста
          </h3>
          <p class="text-neutral-500 mb-6">
            Здесь будут отображаться документы, которые вы удалили
          </p>
          <router-link
            to="/dam"
            class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-xl
                   hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                   transition-all shadow-lg shadow-primary-500/25"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Перейти в галерею
          </router-link>
        </div>
      </div>
      
      <!-- Documents Grid -->
      <div v-else class="space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="relative bg-white rounded-xl border border-neutral-200 overflow-hidden hover:shadow-lg transition-shadow"
          >
            <!-- Checkbox -->
            <div class="absolute top-2 left-2 z-10">
              <input
                type="checkbox"
                :checked="selectedDocuments.includes(doc.id)"
                @change="toggleSelection(doc.id)"
                class="w-5 h-5 rounded border-neutral-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
              />
            </div>
            
            <!-- Thumbnail -->
            <div class="relative aspect-video bg-neutral-100 overflow-hidden">
              <img
                v-if="getDocumentImageUrl(doc)"
                :src="getDocumentImageUrl(doc)"
                :alt="doc.label"
                class="w-full h-full object-cover"
                @error="handleImageError"
              />
              <div v-else class="w-full h-full flex items-center justify-center bg-neutral-100">
                <svg class="w-12 h-12 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            
            <!-- Document Info -->
            <div class="p-3">
              <h3 class="text-sm font-medium text-neutral-900 truncate mb-1">
                {{ doc.label }}
              </h3>
              <p class="text-xs text-neutral-500 mb-2">
                {{ doc.document_type?.label || 'Документ' }}
              </p>
              <p class="text-xs text-neutral-400">
                Удален: {{ formatDate(doc.trashed_date_time) }}
              </p>
              
              <!-- Actions -->
              <div class="flex items-center gap-2 mt-3 pt-3 border-t border-neutral-100">
                <button
                  type="button"
                  class="flex-1 px-2 py-1.5 text-xs font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
                  @click="handleRestore(doc.id)"
                  title="Восстановить"
                >
                  Восстановить
                </button>
                <button
                  type="button"
                  class="flex-1 px-2 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                  @click="handleDelete(doc.id)"
                  title="Удалить навсегда"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Load More -->
        <div v-if="hasMore" class="flex justify-center pt-6">
          <button
            type="button"
            class="px-6 py-3 bg-white border border-neutral-300 rounded-xl text-sm font-medium text-neutral-700 hover:bg-neutral-50 transition-colors"
            @click="loadMore"
            :disabled="isLoading"
          >
            Загрузить ещё
          </button>
        </div>
      </div>
    </div>
    
    <!-- Confirm Modals -->
    <Teleport to="body">
      <!-- Restore Confirmation -->
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showRestoreModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="showRestoreModal = false" />
          <div class="relative w-full max-w-md bg-white rounded-2xl shadow-xl p-6">
            <h3 class="text-lg font-semibold text-neutral-900 mb-4">Восстановить документ?</h3>
            <p class="text-sm text-neutral-600 mb-6">
              Документ будет восстановлен из корзины и снова станет доступен в галерее.
            </p>
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="showRestoreModal = false"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-colors"
                @click="confirmRestore"
              >
                Восстановить
              </button>
            </div>
          </div>
        </div>
      </Transition>
      
      <!-- Delete Confirmation -->
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="showDeleteModal = false" />
          <div class="relative w-full max-w-md bg-white rounded-2xl shadow-xl p-6">
            <h3 class="text-lg font-semibold text-neutral-900 mb-4">Удалить навсегда?</h3>
            <p class="text-sm text-neutral-600 mb-6">
              Документ будет удален безвозвратно. Это действие нельзя отменить.
            </p>
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="showDeleteModal = false"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-red-600 rounded-xl hover:bg-red-700 transition-colors"
                @click="confirmDelete"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      </Transition>
      
      <!-- Empty Trash Confirmation -->
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showEmptyTrashModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="showEmptyTrashModal = false" />
          <div class="relative w-full max-w-md bg-white rounded-2xl shadow-xl p-6">
            <h3 class="text-lg font-semibold text-neutral-900 mb-4">Очистить корзину?</h3>
            <p class="text-sm text-neutral-600 mb-6">
              Все документы в корзине будут удалены навсегда. Это действие нельзя отменить.
            </p>
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="showEmptyTrashModal = false"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-red-600 rounded-xl hover:bg-red-700 transition-colors"
                @click="confirmEmptyTrash"
              >
                Очистить
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'
import { trashService, type TrashedDocument } from '@/services/trashService'

// ============================================================================
// STORES
// ============================================================================

const notificationStore = useNotificationStore()

// ============================================================================
// STATE
// ============================================================================

const documents = ref<TrashedDocument[]>([])
const selectedDocuments = ref<number[]>([])
const isLoading = ref(false)
const hasMore = ref(false)
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(24)

// Modals
const showRestoreModal = ref(false)
const showDeleteModal = ref(false)
const showEmptyTrashModal = ref(false)
const pendingAction = ref<{
  type: 'restore' | 'delete' | 'restore-multiple' | 'delete-multiple' | 'empty'
  documentId?: number
  documentIds?: number[]
} | null>(null)

// ============================================================================
// COMPUTED
// ============================================================================

// ============================================================================
// DATA FETCHING
// ============================================================================

async function fetchDocuments() {
  isLoading.value = true
  try {
    const response = await trashService.getTrashedDocuments({
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: '-trashed_date_time'
    })
    
    if (currentPage.value === 1) {
      documents.value = response.results
    } else {
      documents.value.push(...response.results)
    }
    
    totalCount.value = response.count
    hasMore.value = !!response.next
  } catch (error: any) {
    console.error('Failed to fetch trashed documents:', error)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось загрузить документы из корзины'
    })
  } finally {
    isLoading.value = false
  }
}

async function loadMore() {
  if (hasMore.value && !isLoading.value) {
    currentPage.value++
    await fetchDocuments()
  }
}

// ============================================================================
// HANDLERS
// ============================================================================

function toggleSelection(documentId: number) {
  const index = selectedDocuments.value.indexOf(documentId)
  if (index > -1) {
    selectedDocuments.value.splice(index, 1)
  } else {
    selectedDocuments.value.push(documentId)
  }
}

function handleRestore(documentId: number) {
  pendingAction.value = { type: 'restore', documentId }
  showRestoreModal.value = true
}

function handleRestoreSelected() {
  if (selectedDocuments.value.length === 0) return
  pendingAction.value = { type: 'restore-multiple', documentIds: [...selectedDocuments.value] }
  showRestoreModal.value = true
}

async function confirmRestore() {
  if (!pendingAction.value) return
  
  showRestoreModal.value = false
  
  try {
    if (pendingAction.value.type === 'restore') {
      await trashService.restoreDocument(pendingAction.value.documentId!)
      notificationStore.addNotification({
        type: 'success',
        title: 'Восстановлено',
        message: 'Документ восстановлен из корзины'
      })
    } else if (pendingAction.value.type === 'restore-multiple') {
      await trashService.restoreDocuments(pendingAction.value.documentIds!)
      notificationStore.addNotification({
        type: 'success',
        title: 'Восстановлено',
        message: `Восстановлено документов: ${pendingAction.value.documentIds!.length}`
      })
    }
    
    // Remove restored documents from list
    if (pendingAction.value.type === 'restore') {
      documents.value = documents.value.filter(d => d.id !== pendingAction.value!.documentId)
      selectedDocuments.value = selectedDocuments.value.filter(id => id !== pendingAction.value!.documentId)
    } else {
      documents.value = documents.value.filter(d => !pendingAction.value!.documentIds!.includes(d.id))
      selectedDocuments.value = []
    }
    
    totalCount.value = documents.value.length
  } catch (error: any) {
    console.error('Failed to restore document:', error)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось восстановить документ'
    })
  } finally {
    pendingAction.value = null
  }
}

function handleDelete(documentId: number) {
  pendingAction.value = { type: 'delete', documentId }
  showDeleteModal.value = true
}

function handleDeleteSelected() {
  if (selectedDocuments.value.length === 0) return
  pendingAction.value = { type: 'delete-multiple', documentIds: [...selectedDocuments.value] }
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!pendingAction.value) return
  
  showDeleteModal.value = false
  
  try {
    if (pendingAction.value.type === 'delete') {
      await trashService.deleteDocument(pendingAction.value.documentId!)
      notificationStore.addNotification({
        type: 'success',
        title: 'Удалено',
        message: 'Документ удален навсегда'
      })
    } else if (pendingAction.value.type === 'delete-multiple') {
      await trashService.deleteDocuments(pendingAction.value.documentIds!)
      notificationStore.addNotification({
        type: 'success',
        title: 'Удалено',
        message: `Удалено документов: ${pendingAction.value.documentIds!.length}`
      })
    }
    
    // Remove deleted documents from list
    if (pendingAction.value.type === 'delete') {
      documents.value = documents.value.filter(d => d.id !== pendingAction.value!.documentId)
      selectedDocuments.value = selectedDocuments.value.filter(id => id !== pendingAction.value!.documentId)
    } else {
      documents.value = documents.value.filter(d => !pendingAction.value!.documentIds!.includes(d.id))
      selectedDocuments.value = []
    }
    
    totalCount.value = documents.value.length
  } catch (error: any) {
    console.error('Failed to delete document:', error)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось удалить документ'
    })
  } finally {
    pendingAction.value = null
  }
}

function handleEmptyTrash() {
  showEmptyTrashModal.value = true
}

async function confirmEmptyTrash() {
  showEmptyTrashModal.value = false
  
  try {
    await trashService.emptyTrash()
    documents.value = []
    selectedDocuments.value = []
    totalCount.value = 0
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Корзина очищена',
      message: 'Все документы удалены навсегда'
    })
  } catch (error: any) {
    console.error('Failed to empty trash:', error)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось очистить корзину'
    })
  }
}

function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

function getDocumentImageUrl(doc: TrashedDocument): string | null {
  // Use image_url from API if available, otherwise construct it
  if (doc.image_url) {
    return doc.image_url
  }
  return trashService.getDocumentImageUrl(doc.id)
}

// ============================================================================
// UTILS
// ============================================================================

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function pluralize(count: number, one: string, few: string, many: string): string {
  const mod10 = count % 10
  const mod100 = count % 100
  
  if (mod100 >= 11 && mod100 <= 19) {
    return many
  }
  
  if (mod10 === 1) {
    return one
  }
  
  if (mod10 >= 2 && mod10 <= 4) {
    return few
  }
  
  return many
}

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.collection-browser {
  min-height: calc(100vh - 4rem);
}
</style>

