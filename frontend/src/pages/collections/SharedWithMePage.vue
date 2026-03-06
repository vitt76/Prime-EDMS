<template>
  <CollectionBrowser
    title="Доступные мне"
    subtitle="Файлы, которыми с вами поделились коллеги"
    :assets="assets"
    :total-count="totalCount"
    :is-loading="isLoading"
    :has-more="false"
    :show-favorite-button="true"
    :show-owner="false"
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
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CollectionBrowser from '@/components/collections/CollectionBrowser.vue'
import { apiService } from '@/services/apiService'
import { cabinetService } from '@/services/cabinetService'
import { collectionsService } from '@/services/collectionsService'
import type { ExtendedAsset } from '@/types/api'
import { useNotificationStore } from '@/stores/notificationStore'

const router = useRouter()
const notificationStore = useNotificationStore()

const assets = ref<ExtendedAsset[]>([])
const totalCount = ref(0)
const isLoading = ref(false)

async function fetchSharedWithMe() {
  isLoading.value = true

  try {
    const sharedCabinets = await cabinetService.getSharedWithMeCabinets()
    const cabinetAssets = await Promise.all(
      sharedCabinets.map(async (cabinet) => {
        const response = await collectionsService.getCollectionAssets({
          collection_id: String(cabinet.id),
          limit: 20
        })

        return response.results.map((asset) => ({
          ...asset,
          sharedWithMe: true
        } as ExtendedAsset))
      })
    )

    const deduplicated = new Map<number, ExtendedAsset>()
    cabinetAssets.flat().forEach((asset) => {
      if (!deduplicated.has(asset.id)) {
        deduplicated.set(asset.id, asset)
      }
    })

    assets.value = Array.from(deduplicated.values())
    totalCount.value = assets.value.length
  } catch (error) {
    console.error('[SharedWithMe] Failed to load shared assets', error)
    assets.value = []
    totalCount.value = 0
    notificationStore.addNotification({
      type: 'error',
      title: 'Доступные мне недоступны',
      message: 'Не удалось загрузить подборки, которыми с вами поделились.'
    })
  } finally {
    isLoading.value = false
  }
}

async function handleToggleFavorite(asset: ExtendedAsset) {
  try {
    if (asset.isFavorite) {
      await apiService.post(`/api/v4/documents/${asset.id}/remove_from_favorites/`, {})
      asset.isFavorite = false
    } else {
      await apiService.post(`/api/v4/documents/${asset.id}/add_to_favorites/`, {})
      asset.isFavorite = true
    }

    assets.value = assets.value.map((item) =>
      item.id === asset.id ? { ...item, isFavorite: asset.isFavorite } : item
    )

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

onMounted(() => {
  fetchSharedWithMe()
})
</script>

