<template>
  <Transition
    enter-active-class="transform transition-all duration-300 ease-out"
    enter-from-class="translate-y-full opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transform transition-all duration-200 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-full opacity-0"
  >
    <div
      v-if="selectedCount > 0"
      class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[1000]
             bg-neutral-900/90 backdrop-blur-xl 
             rounded-2xl shadow-2xl shadow-black/30
             border border-neutral-700/50
             px-6 py-4 flex items-center gap-6"
    >
      <!-- Selection Info -->
      <div class="flex items-center gap-3 pr-6 border-r border-neutral-700">
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary-500/20 text-primary-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <p class="text-white font-semibold text-sm">
            {{ selectedCount }} {{ selectedLabel }}
          </p>
          <p class="text-neutral-400 text-xs">
            Выбрано
          </p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <!-- Favorite -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-neutral-800 hover:bg-neutral-700 
                 text-white text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="handleFavorite"
          :disabled="isLoading"
          title="В избранное"
        >
          <svg class="w-4 h-4" :fill="'currentColor'" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <span class="hidden sm:inline">Избранное</span>
        </button>
        <!-- Download -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-neutral-800 hover:bg-neutral-700 
                 text-white text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="handleDownload"
          :disabled="isLoading"
          title="Скачать как ZIP"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span class="hidden sm:inline">Скачать</span>
        </button>

        <!-- Share -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-neutral-800 hover:bg-neutral-700 
                 text-white text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="handleShare"
          :disabled="isLoading"
          title="Поделиться"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <span class="hidden sm:inline">Поделиться</span>
        </button>

        <!-- Tag -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-neutral-800 hover:bg-neutral-700 
                 text-white text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="handleTag"
          :disabled="isLoading"
          title="Добавить теги"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          <span class="hidden sm:inline">Теги</span>
        </button>

        <!-- Move -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-neutral-800 hover:bg-neutral-700 
                 text-white text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="handleMove"
          :disabled="isLoading"
          title="Переместить"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
          <span class="hidden sm:inline">Переместить</span>
        </button>

        <!-- Delete -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-red-500/20 hover:bg-red-500/30 
                 text-red-400 hover:text-red-300 text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="handleDelete"
          :disabled="isLoading"
          title="Удалить"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span class="hidden sm:inline">Удалить</span>
        </button>
      </div>

      <!-- Clear Selection -->
      <button
        class="ml-2 p-2.5 rounded-xl
               bg-neutral-800 hover:bg-neutral-700 
               text-neutral-400 hover:text-white
               transition-all duration-200"
        @click="handleClearSelection"
        title="Снять выделение"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </Transition>

  <!-- Bulk Tag Modal -->
  <BulkTagModal
    :is-open="showTagModal"
    :selected-count="selectedCount"
    :selected-ids="selectedIds"
    @close="showTagModal = false"
    @success="handleTagSuccess"
  />

  <!-- Delete Confirmation Modal -->
  <ConfirmModal
    :is-open="showDeleteConfirm"
    title="Удалить выбранные активы?"
    :message="`Вы собираетесь удалить ${selectedCount} актив(ов). Это действие нельзя отменить.`"
    confirm-text="Удалить"
    confirm-variant="danger"
    @close="showDeleteConfirm = false"
    @confirm="confirmDelete"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAssetStore } from '@/stores/assetStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useNotificationStore } from '@/stores/notificationStore'
import BulkTagModal from './BulkTagModal.vue'
import ConfirmModal from '@/components/Common/ConfirmModal.vue'

const emit = defineEmits<{
  share: []
  download: []
  move: []
  favorite: []
}>()

const assetStore = useAssetStore()
const favoritesStore = useFavoritesStore()
const notificationStore = useNotificationStore()

const isLoading = ref(false)
const showTagModal = ref(false)
const showDeleteConfirm = ref(false)

const selectedCount = computed(() => assetStore.selectedAssets.size)
const selectedIds = computed(() => Array.from(assetStore.selectedAssets))

const selectedLabel = computed(() => {
  const count = selectedCount.value
  if (count === 1) return 'актив'
  if (count >= 2 && count <= 4) return 'актива'
  return 'активов'
})

function handleDownload() {
  isLoading.value = true
  
  // Simulate ZIP creation delay
  setTimeout(() => {
    isLoading.value = false
    notificationStore.addNotification({
      type: 'success',
      title: 'Загрузка началась',
      message: `Подготовка ZIP-архива с ${selectedCount.value} файлами...`,
    })
    
    // Simulate download completion
    setTimeout(() => {
      notificationStore.addNotification({
        type: 'info',
        title: 'Архив готов',
        message: 'assets_selected.zip (12.5 MB) загружен',
      })
    }, 2000)
    
    emit('download')
  }, 800)
}

function handleShare() {
  emit('share')
}

function handleTag() {
  showTagModal.value = true
}

function handleTagSuccess(tags: string[]) {
  showTagModal.value = false
  notificationStore.addNotification({
    type: 'success',
    title: 'Теги добавлены',
    message: `Теги "${tags.join(', ')}" добавлены к ${selectedCount.value} активам`,
  })
  assetStore.clearSelection()
}

function handleMove() {
  notificationStore.addNotification({
    type: 'info',
    title: 'Функция в разработке',
    message: 'Массовое перемещение будет доступно в следующем обновлении',
  })
  emit('move')
}

async function handleFavorite() {
  isLoading.value = true
  try {
    const ids = selectedIds.value
    for (const id of ids) {
      if (!favoritesStore.isFavorite(id)) {
        await favoritesStore.toggleFavorite(id)
      }
    }
    notificationStore.addNotification({
      type: 'success',
      title: 'Избранное обновлено',
      message: `Добавлено в избранное: ${ids.length} актив(ов)`
    })
    emit('favorite')
  } catch (error: any) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка избранного',
      message: error?.message || 'Не удалось обновить избранное'
    })
  } finally {
    isLoading.value = false
  }
}

function handleDelete() {
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  isLoading.value = true
  showDeleteConfirm.value = false
  
  try {
    const ids = selectedIds.value
    
    // Use assetStore.bulkDelete
    const deletedCount = await assetStore.bulkDelete(ids)
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Активы удалены',
      message: `${deletedCount} активов успешно удалено`,
    })
    
    assetStore.clearSelection()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка удаления',
      message: 'Не удалось удалить выбранные активы',
    })
  } finally {
    isLoading.value = false
  }
}

function handleClearSelection() {
  assetStore.clearSelection()
}
</script>

