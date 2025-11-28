import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { distributionService } from '@/services/distributionService'
import type { Publication, PaginatedResponse, Asset } from '@/types/api'
import { formatApiError } from '@/utils/errors'
import {
  getMockSharedLinks,
  getMockSharedLinkById,
  createMockSharedLink,
  revokeMockSharedLink,
  updateMockSharedLink,
  getSharedAssetIds,
  isAssetShared,
  type SharedLink,
  type CreateSharedLinkParams
} from '@/mocks/publications'

export type { SharedLink, CreateSharedLinkParams }

export const useDistributionStore = defineStore(
  'distribution',
  () => {
    // ==================== State ====================
    
    // Publications (existing)
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

    // Shared Links (new)
    const sharedLinks = ref<SharedLink[]>([])
    const sharedLinksLoading = ref(false)
    const sharedLinksError = ref<string | null>(null)
    const sharedLinkFilters = ref<{
      status?: SharedLink['status']
      search?: string
    }>({})

    // ==================== Getters ====================

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

    // Shared links getters
    const activeSharedLinks = computed(() => 
      sharedLinks.value.filter(link => link.status === 'active')
    )

    const expiredSharedLinks = computed(() => 
      sharedLinks.value.filter(link => link.status === 'expired')
    )

    const revokedSharedLinks = computed(() => 
      sharedLinks.value.filter(link => link.status === 'revoked')
    )

    const sharedAssetIds = computed(() => getSharedAssetIds())

    // Mock data for dev mode
    const mockPublications: Publication[] = [
      {
        id: 1,
        title: 'Пресс-релиз: Новый продукт 2025',
        description: 'Официальный пресс-релиз о запуске нового продукта',
        status: 'published',
        created_date: new Date(Date.now() - 86400000).toISOString(),
        updated_date: new Date().toISOString(),
        published_date: new Date().toISOString(),
        created_by: 'admin',
        created_by_id: 1,
        assets: [],
        channels: [{ id: 1, name: 'Веб-сайт', type: 'website', status: 'active' }],
        analytics: { views: 1250, downloads: 87, shares: 23 }
      },
      {
        id: 2,
        title: 'Маркетинговые материалы Q1',
        description: 'Набор маркетинговых материалов для первого квартала',
        status: 'draft',
        created_date: new Date(Date.now() - 172800000).toISOString(),
        updated_date: new Date(Date.now() - 86400000).toISOString(),
        created_by: 'editor',
        created_by_id: 2,
        assets: [],
        channels: []
      },
      {
        id: 3,
        title: 'Корпоративная презентация',
        description: 'Обновленная корпоративная презентация компании',
        status: 'scheduled',
        created_date: new Date(Date.now() - 259200000).toISOString(),
        updated_date: new Date(Date.now() - 172800000).toISOString(),
        created_by: 'manager',
        created_by_id: 3,
        assets: [],
        channels: [{ id: 2, name: 'Email', type: 'email', status: 'active' }]
      }
    ] as Publication[]

    // ==================== Publications Actions ====================

    async function fetchPublications(params?: {
      page?: number
      page_size?: number
      status?: Publication['status']
      search?: string
    }) {
      isLoading.value = true
      error.value = null

      try {
        // In dev mode, use mock data
        if (import.meta.env.DEV) {
          await new Promise(resolve => setTimeout(resolve, 300))
          publications.value = mockPublications
          totalCount.value = mockPublications.length
          return
        }

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
        // In dev mode, fallback to mock data
        if (import.meta.env.DEV) {
          console.warn('[Dev] Using mock publications')
          publications.value = mockPublications
          totalCount.value = mockPublications.length
          return
        }
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

    // ==================== Shared Links Actions ====================

    /**
     * Fetch all shared links
     */
    async function fetchSharedLinks(filters?: {
      status?: SharedLink['status']
      search?: string
    }) {
      sharedLinksLoading.value = true
      sharedLinksError.value = null

      try {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 300))
        
        sharedLinks.value = getMockSharedLinks(filters)
        sharedLinkFilters.value = filters || {}
      } catch (err) {
        sharedLinksError.value = formatApiError(err)
        sharedLinks.value = []
      } finally {
        sharedLinksLoading.value = false
      }
    }

    /**
     * Get a single shared link by ID
     */
    function getSharedLink(id: number): SharedLink | undefined {
      return getMockSharedLinkById(id)
    }

    /**
     * Create a new shared link
     */
    async function createSharedLink(params: CreateSharedLinkParams): Promise<SharedLink> {
      sharedLinksLoading.value = true
      sharedLinksError.value = null

      try {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const newLink = createMockSharedLink(params)
        
        // Add to local state
        sharedLinks.value.unshift(newLink)
        
        return newLink
      } catch (err) {
        sharedLinksError.value = formatApiError(err)
        throw err
      } finally {
        sharedLinksLoading.value = false
      }
    }

    /**
     * Revoke (delete) a shared link
     */
    async function revokeSharedLink(id: number): Promise<boolean> {
      sharedLinksLoading.value = true
      sharedLinksError.value = null

      try {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 300))
        
        const success = revokeMockSharedLink(id)
        
        if (success) {
          // Update local state
          const index = sharedLinks.value.findIndex(link => link.id === id)
          if (index !== -1) {
            sharedLinks.value[index].status = 'revoked'
          }
        }
        
        return success
      } catch (err) {
        sharedLinksError.value = formatApiError(err)
        throw err
      } finally {
        sharedLinksLoading.value = false
      }
    }

    /**
     * Update a shared link
     */
    async function updateSharedLink(
      id: number,
      updates: Partial<Pick<SharedLink, 'name' | 'expires_date' | 'allow_download' | 'allow_comment'>>
    ): Promise<SharedLink | undefined> {
      sharedLinksLoading.value = true
      sharedLinksError.value = null

      try {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 300))
        
        const updated = updateMockSharedLink(id, updates)
        
        if (updated) {
          // Update local state
          const index = sharedLinks.value.findIndex(link => link.id === id)
          if (index !== -1) {
            sharedLinks.value[index] = updated
          }
        }
        
        return updated
      } catch (err) {
        sharedLinksError.value = formatApiError(err)
        throw err
      } finally {
        sharedLinksLoading.value = false
      }
    }

    /**
     * Apply filters to shared links
     */
    function applySharedLinkFilters(filters: typeof sharedLinkFilters.value) {
      sharedLinkFilters.value = { ...sharedLinkFilters.value, ...filters }
      fetchSharedLinks(sharedLinkFilters.value)
    }

    /**
     * Clear shared link filters
     */
    function clearSharedLinkFilters() {
      sharedLinkFilters.value = {}
      fetchSharedLinks()
    }

    /**
     * Check if an asset is currently shared
     */
    function checkAssetShared(assetId: number): boolean {
      return isAssetShared(assetId)
    }

    /**
     * Refresh shared links
     */
    function refreshSharedLinks() {
      fetchSharedLinks(sharedLinkFilters.value)
    }

    return {
      // Publications State
      publications,
      totalCount,
      currentPage,
      pageSize,
      isLoading,
      error,
      currentPublication,
      filters,

      // Publications Getters
      hasNextPage,
      hasPreviousPage,
      totalPages,

      // Publications Actions
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
      refresh,

      // Shared Links State
      sharedLinks,
      sharedLinksLoading,
      sharedLinksError,
      sharedLinkFilters,

      // Shared Links Getters
      activeSharedLinks,
      expiredSharedLinks,
      revokedSharedLinks,
      sharedAssetIds,

      // Shared Links Actions
      fetchSharedLinks,
      getSharedLink,
      createSharedLink,
      revokeSharedLink,
      updateSharedLink,
      applySharedLinkFilters,
      clearSharedLinkFilters,
      checkAssetShared,
      refreshSharedLinks
    }
  },
  {
    persist: {
      paths: ['pageSize', 'filters', 'sharedLinkFilters'] // Persist user preferences
    }
  }
)
