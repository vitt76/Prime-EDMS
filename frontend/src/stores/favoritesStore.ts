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
    if (value) {
      favoriteIds.value.add(id)
    } else {
      favoriteIds.value.delete(id)
    }
  }

  const fetchFavorites = async () => {
    isLoading.value = true
    error.value = null
    try {
      const ids = await apiService.get<number[]>('/api/v4/headless/favorites/')
      favoriteIds.value = new Set(ids)
    } catch (err: any) {
      error.value = err?.message || 'Не удалось загрузить избранное'
      favoriteIds.value.clear()
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

