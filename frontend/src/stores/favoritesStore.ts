import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService } from '@/services/apiService'
import { adaptBackendAsset } from '@/services/adapters/mayanAdapter'
import type { Asset } from '@/types/api'

export const useFavoritesStore = defineStore('favorites', () => {
  const favoriteIds = ref<Set<number>>(new Set())
  const favoriteAssets = ref<Asset[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isFavorite = (documentId: number | string): boolean => {
    return favoriteIds.value.has(Number(documentId))
  }

  const setFavorite = (documentId: number, value: boolean) => {
    const id = Number(documentId)
    const next = new Set(favoriteIds.value)
    if (value) {
      next.add(id)
    } else {
      next.delete(id)
    }
    favoriteIds.value = next
  }

  const fetchFavorites = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiService.get<any>('/api/v4/headless/favorites/', {
        params: { page_size: 200 }
      })

      let ids: number[] = []
      let assets: Asset[] = []

      if (Array.isArray(response?.results)) {
        ids = response.results
          .map((item: any) => Number(item?.document?.id ?? item?.id))
          .filter((id: number) => !Number.isNaN(id))

        assets = response.results
          .map((item: any) => item?.document)
          .filter((doc: any) => !!doc)
          .map((doc: any) => adaptBackendAsset(doc))
      } else if (Array.isArray(response)) {
        ids = response.map((value: any) => Number(value)).filter((id: number) => !Number.isNaN(id))
      }

      favoriteIds.value = new Set(ids)
      favoriteAssets.value = assets
    } catch (err: any) {
      error.value = err?.message || 'Не удалось загрузить избранное'
      favoriteIds.value = new Set()
      favoriteAssets.value = []
    } finally {
      isLoading.value = false
    }
  }

  const toggleFavorite = async (documentId: number): Promise<boolean> => {
    const id = Number(documentId)
    const optimistic = !isFavorite(id)
    setFavorite(id, optimistic)

    try {
      const resp = await apiService.post<{ favorited: boolean }>(
        `/api/v4/headless/favorites/${id}/`,
        {}
      )
      setFavorite(id, resp.favorited)

      if (resp.favorited === false) {
        favoriteAssets.value = favoriteAssets.value.filter(asset => asset.id !== id)
      }

      return resp.favorited
    } catch (err) {
      // revert on error
      setFavorite(id, !optimistic)
      throw err
    }
  }

  return {
    favoriteIds,
    favoriteAssets,
    isLoading,
    error,
    isFavorite,
    fetchFavorites,
    toggleFavorite,
    setFavorite
  }
})

