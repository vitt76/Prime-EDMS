<template>
  <div class="dam-page">
    <GalleryView 
      @open-upload="$emit('open-upload')"
      @delete="handleAssetDelete"
    />
    
    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :is-open="showDeleteConfirm"
      title="Удалить документ?"
      :message="deleteTarget ? `${deleteTarget.label} будет удалён вместе с файлами и версиями. Действие необратимо.` : 'Удалить документ?'"
      confirm-text="Удалить"
      confirm-variant="danger"
      @close="cancelDelete"
      @confirm="confirmDelete"
    />
    
    <!-- API Debug Panel (DEV only) - lazy loaded -->
    <Suspense v-if="isDev">
      <template #default>
        <ApiDebugPanel />
      </template>
      <template #fallback>
        <div></div>
      </template>
    </Suspense>
  </div>
</template>

<script setup lang="ts">
import { ref, defineAsyncComponent, onMounted } from 'vue'
import { onBeforeRouteUpdate } from 'vue-router'
import GalleryView from '@/components/DAM/GalleryView.vue'
import ConfirmModal from '@/components/Common/ConfirmModal.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useNotificationStore } from '@/stores/notificationStore'
import type { Asset } from '@/types/api'

// Lazy load debug panel to avoid blocking main page
const ApiDebugPanel = defineAsyncComponent(() => 
  import('@/components/Debug/ApiDebugPanel.vue')
)

const isDev = ref(import.meta.env.DEV)
const assetStore = useAssetStore()
const favoritesStore = useFavoritesStore()
const notificationStore = useNotificationStore()
const showDeleteConfirm = ref(false)
const deleteTarget = ref<Asset | null>(null)

onMounted(() => {
  // При заходе в основную галерею сбрасываем фильтр по папкам
  assetStore.setFolderFilter(null, null)
  assetStore.fetchAssets({ page: 1 })
  favoritesStore.fetchFavorites()
})

onBeforeRouteUpdate(() => {
  // При возврате на /dam обновим избранное и сбросим фильтр
  assetStore.setFolderFilter(null, null)
  favoritesStore.fetchFavorites()
})

function handleAssetDelete(asset: Asset): void {
  deleteTarget.value = asset
  showDeleteConfirm.value = true
}

async function confirmDelete(): Promise<void> {
  if (!deleteTarget.value) return
  const target = deleteTarget.value
  showDeleteConfirm.value = false
  const ok = await assetStore.deleteAsset(target.id)
  if (ok) {
    notificationStore.addNotification({
      type: 'success',
      title: 'Документ удалён',
      message: `"${target.label}" удалён вместе с файлами и версиями`
    })
  }
  deleteTarget.value = null
}

function cancelDelete(): void {
  showDeleteConfirm.value = false
  deleteTarget.value = null
}

defineEmits<{
  'open-upload': []
}>()
</script>

<style scoped>
.dam-page {
  width: 100%;
  min-height: 100vh;
}
</style>

