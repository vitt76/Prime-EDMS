import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { distributionService } from '@/services/distributionService'
import type { Publication, PaginatedResponse } from '@/types/api'
import { formatApiError } from '@/utils/errors'

export const useDistributionStore = defineStore(
  'distribution',
  () => {
    // State
    const publications = ref<Publication[]>([])
    const totalCount = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const currentPublication = ref<Publication | null>(null)
    const filters = ref<{
      status?: Publication['status']
      search?: string
    }>({})

    // Getters
    const hasNextPage = computed(() => {
      const totalPages = Math.ceil(totalCount.value / pageSize.value)
      return currentPage.value < totalPages
    })

    const hasPreviousPage = computed(() => {
      return currentPage.value > 1
    })

    const totalPages = computed(() => {
      return Math.ceil(totalCount.value / pageSize.value)
    })

    // Actions
    async function fetchPublications(params?: {
      page?: number
      page_size?: number
      status?: Publication['status']
      search?: string
    }) {
      isLoading.value = true
      error.value = null

      try {
        const queryParams = {
          page: currentPage.value,
          page_size: pageSize.value,
          ...filters.value,
          ...params
        }

        const response: PaginatedResponse<Publication> = await distributionService.getPublications(
          queryParams
        )

        publications.value = response.results
        totalCount.value = response.count

        if (params?.page) {
          currentPage.value = params.page
        }
      } catch (err) {
        error.value = formatApiError(err)
        publications.value = []
        totalCount.value = 0
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function getPublication(id: number) {
      isLoading.value = true
      error.value = null

      try {
        const publication = await distributionService.getPublication(id)
        currentPublication.value = publication
        return publication
      } catch (err) {
        error.value = formatApiError(err)
        currentPublication.value = null
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function createPublication(publication: Parameters<typeof distributionService.createPublication>[0]) {
      isLoading.value = true
      error.value = null

      try {
        const newPublication = await distributionService.createPublication(publication)
        publications.value.unshift(newPublication)
        totalCount.value++
        return newPublication
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function updatePublication(
      id: number,
      publication: Parameters<typeof distributionService.updatePublication>[1]
    ) {
      isLoading.value = true
      error.value = null

      try {
        const updated = await distributionService.updatePublication(id, publication)
        const index = publications.value.findIndex((p) => p.id === id)
        if (index !== -1) {
          publications.value[index] = updated
        }
        if (currentPublication.value?.id === id) {
          currentPublication.value = updated
        }
        return updated
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function deletePublication(id: number) {
      isLoading.value = true
      error.value = null

      try {
        await distributionService.deletePublication(id)
        publications.value = publications.value.filter((p) => p.id !== id)
        totalCount.value--
        if (currentPublication.value?.id === id) {
          currentPublication.value = null
        }
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function publishPublication(id: number) {
      isLoading.value = true
      error.value = null

      try {
        const published = await distributionService.publishPublication(id)
        const index = publications.value.findIndex((p) => p.id === id)
        if (index !== -1) {
          publications.value[index] = published
        }
        if (currentPublication.value?.id === id) {
          currentPublication.value = published
        }
        return published
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    function setPage(page: number) {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        fetchPublications()
      }
    }

    function setPageSize(size: number) {
      pageSize.value = Math.min(Math.max(size, 1), 100)
      currentPage.value = 1
      fetchPublications()
    }

    function applyFilters(newFilters: typeof filters.value) {
      filters.value = { ...filters.value, ...newFilters }
      currentPage.value = 1
      fetchPublications()
    }

    function clearFilters() {
      filters.value = {}
      currentPage.value = 1
      fetchPublications()
    }

    function refresh() {
      fetchPublications()
    }

    return {
      // State
      publications,
      totalCount,
      currentPage,
      pageSize,
      isLoading,
      error,
      currentPublication,
      filters,

      // Getters
      hasNextPage,
      hasPreviousPage,
      totalPages,

      // Actions
      fetchPublications,
      getPublication,
      createPublication,
      updatePublication,
      deletePublication,
      publishPublication,
      setPage,
      setPageSize,
      applyFilters,
      clearFilters,
      refresh
    }
  },
  {
    persist: {
      paths: ['pageSize', 'filters'] // Persist user preferences
    }
  }
)

