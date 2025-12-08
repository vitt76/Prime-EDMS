import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService } from '@/services/apiService'

export const useFavoritesStore = defineStore('favorites', () => {
  const favoriteIds = ref<Set<number>>(new Set())
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
      if (Array.isArray(response)) {
        ids = response.map((value: any) => Number(value))
      } else if (Array.isArray(response?.results)) {
        ids = response.results
          .map((item: any) => Number(item?.document?.id ?? item?.id))
          .filter((id: number) => !Number.isNaN(id))
      }

      favoriteIds.value = new Set(ids)
    } catch (err: any) {
      error.value = err?.message || 'Не удалось загрузить избранное'
      favoriteIds.value = new Set()
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
      return resp.favorited
    } catch (err) {
      // revert on error
      setFavorite(id, !optimistic)
      throw err
    }
  }

  return {
    favoriteIds,
    isLoading,
    error,
    isFavorite,
    fetchFavorites,
    toggleFavorite,
    setFavorite
  }
})

