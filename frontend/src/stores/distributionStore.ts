import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { distributionService } from '@/services/distributionService'
import type { Publication, PaginatedResponse, Asset, DistributionCampaign } from '@/types/api'
import { formatApiError } from '@/utils/errors'
import { adaptShareLink, adaptShareLinks, type APIShareLink } from '@/utils/shareLinkAdapter'
import {
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

    // Shared Links (public links)
    const sharedLinks = ref<SharedLink[]>([])
    const sharedLinksLoading = ref(false)
    const sharedLinksError = ref<string | null>(null)
    const sharedLinkFilters = ref<{
      status?: SharedLink['status']
      search?: string
    }>({})

    // Campaigns
    const campaigns = ref<DistributionCampaign[]>([])
    const campaignsLoading = ref(false)
    const campaignsError = ref<string | null>(null)

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

    const sharedAssetIds = computed(() => new Set(getSharedAssetIds()))

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
     * Fetch all shared links from API
     */
    async function fetchSharedLinks(filters?: {
      status?: SharedLink['status']
      search?: string
    }) {
      sharedLinksLoading.value = true
      sharedLinksError.value = null

      try {
        // Fetch from real API
        console.log('[DistributionStore] Fetching shared links from API...')
        const response = await distributionService.getAllShareLinks({
          page_size: 100 // Get all links for now
        })
        
        console.log('[DistributionStore] API response:', {
          count: response.count,
          resultsCount: response.results?.length || 0,
          results: response.results
        })
        
        // Adapt API response to Vue format
        const baseUrl = window.location.origin
        let adaptedLinks = adaptShareLinks(response.results || [], baseUrl)
        
        console.log('[DistributionStore] Adapted links:', adaptedLinks.length, adaptedLinks)
        
        // Apply filters if provided
        if (filters?.status) {
          adaptedLinks = adaptedLinks.filter(link => link.status === filters.status)
        }
        
        if (filters?.search) {
          const query = filters.search.toLowerCase()
          adaptedLinks = adaptedLinks.filter(link =>
            link.name.toLowerCase().includes(query) ||
            link.slug.toLowerCase().includes(query) ||
            link.created_by.toLowerCase().includes(query)
          )
        }
        
        sharedLinks.value = adaptedLinks
        sharedLinkFilters.value = filters || {}
      } catch (err) {
        sharedLinksError.value = formatApiError(err)
        sharedLinks.value = []
        // Do not crash / spam; this endpoint can be unstable depending on backend state.
        console.warn('[DistributionStore] Failed to fetch shared links (non-fatal):', err)
      } finally {
        sharedLinksLoading.value = false
      }
    }

    /**
     * Get a single shared link by ID
     */
    async function getSharedLink(id: number): Promise<SharedLink | undefined> {
      try {
        const apiLink = await distributionService.getShareLinkById(id)
        const baseUrl = window.location.origin
        return adaptShareLink(apiLink, baseUrl)
      } catch (err) {
        console.error('Failed to fetch shared link:', err)
        return undefined
      }
    }

    /**
     * Create a new shared link
     * Uses simplified endpoint that automatically creates publication and renditions
     */
    async function createSharedLink(params: CreateSharedLinkParams & { rendition_id?: number, publication_id?: number }): Promise<SharedLink> {
      sharedLinksLoading.value = true
      sharedLinksError.value = null

      try {
        // If rendition_id is provided, use direct creation
        if (params.rendition_id) {
          const apiLink = await distributionService.createShareLink({
            rendition: params.rendition_id,
            expires_at: params.expires_date || null,
            max_downloads: null
          })
          
          const baseUrl = window.location.origin
          const newLink = adaptShareLink(apiLink, baseUrl)
          sharedLinks.value.unshift(newLink)
          return newLink
        }
        
        // Otherwise, use simplified endpoint that creates everything automatically
        if (!params.asset_ids || params.asset_ids.length === 0) {
          throw new Error('No assets selected for sharing')
        }
        
        // Use simplified endpoint
        // Note: params.asset_ids now contains document_file_ids (active version files)
        const response = await distributionService.createShareLinkSimple({
          document_file_ids: params.asset_ids, // These are document_file_ids, not document_ids
          publication_id: params.publication_id, // Use existing publication if provided
          title: params.name || 'Share Link',
          expires_at: params.expires_date || null,
          max_downloads: params.max_downloads || null,
          max_views: params.max_views || null,
          password: params.password,
          allow_download: params.allow_download !== false
        })
        
        // Response can be a single link or multiple links
        const apiLink = response.share_links ? response.share_links[0] : response
        const baseUrl = window.location.origin
        const newLink = adaptShareLink(apiLink, baseUrl)
        
        // Update name if provided
        if (params.name) {
          newLink.name = params.name
        }
        
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
        // Delete via API
        await distributionService.deleteShareLink(id)
        
        // Remove from local state
        const index = sharedLinks.value.findIndex(link => link.id === id)
        if (index !== -1) {
          sharedLinks.value.splice(index, 1)
        }
        
        return true
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
      updates: Partial<Pick<SharedLink, 'name' | 'expires_date' | 'allow_download' | 'allow_comment' | 'max_views' | 'max_downloads'> & { password?: string }>
    ): Promise<SharedLink | undefined> {
      sharedLinksLoading.value = true
      sharedLinksError.value = null

      try {
        // Prepare API update payload
        const apiUpdates: {
          expires_at?: string | null
          max_downloads?: number | null
          max_views?: number | null
          password?: string
          allow_download?: boolean
        } = {}
        
        if (updates.expires_date !== undefined) {
          // expires_date is already in ISO format from frontend
          apiUpdates.expires_at = updates.expires_date
        }
        
        if (updates.max_downloads !== undefined) {
          apiUpdates.max_downloads = updates.max_downloads || null
        }
        
        if (updates.max_views !== undefined) {
          apiUpdates.max_views = updates.max_views || null
        }
        
        if (updates.password !== undefined) {
          // Send empty string to clear password, or actual password to set it
          // Don't convert empty string to undefined, as we need to explicitly clear the password
          apiUpdates.password = updates.password
        }
        
        if (updates.allow_download !== undefined) {
          apiUpdates.allow_download = updates.allow_download
        }
        
        // Update via API
        const apiLink = await distributionService.updateShareLink(id, apiUpdates)
        
        // Adapt and update local state
        const baseUrl = window.location.origin
        const updated = adaptShareLink(apiLink, baseUrl)
        
        const index = sharedLinks.value.findIndex(link => link.id === id)
        if (index !== -1) {
          sharedLinks.value[index] = updated
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

    // ==================== Campaigns Actions ====================

    async function fetchCampaigns(params?: {
      page?: number
      page_size?: number
      state?: DistributionCampaign['state'] | 'all'
      search?: string
    }) {
      campaignsLoading.value = true
      campaignsError.value = null

      try {
        const response = await distributionService.getCampaigns(params)
        campaigns.value = response.results || []
      } catch (err) {
        campaignsError.value = formatApiError(err)
        campaigns.value = []
        // Для UX достаточно логирования; ошибка может быть показана на UI позже
        console.error('Failed to fetch campaigns:', err)
      } finally {
        campaignsLoading.value = false
      }
    }

    async function createCampaign(payload: {
      title: string
      description?: string
      document_ids?: number[]
    }): Promise<DistributionCampaign | null> {
      campaignsLoading.value = true
      campaignsError.value = null

      try {
        const campaign = await distributionService.createCampaign({
          title: payload.title,
          description: payload.description,
          document_ids: payload.document_ids
        })
        campaigns.value.unshift(campaign)
        return campaign
      } catch (err) {
        campaignsError.value = formatApiError(err)
        console.error('Failed to create campaign:', err)
        return null
      } finally {
        campaignsLoading.value = false
      }
    }

    async function updateCampaign(
      id: number,
      payload: Partial<Pick<DistributionCampaign, 'title' | 'description' | 'state'>>
    ): Promise<DistributionCampaign | null> {
      campaignsLoading.value = true
      campaignsError.value = null

      try {
        const updated = await distributionService.updateCampaign(id, payload)
        const index = campaigns.value.findIndex(c => c.id === id)
        if (index !== -1) {
          campaigns.value[index] = updated
        }
        return updated
      } catch (err) {
        campaignsError.value = formatApiError(err)
        console.error('Failed to update campaign:', err)
        return null
      } finally {
        campaignsLoading.value = false
      }
    }

    async function deleteCampaign(id: number): Promise<boolean> {
      campaignsLoading.value = true
      campaignsError.value = null

      try {
        await distributionService.deleteCampaign(id)
        campaigns.value = campaigns.value.filter(c => c.id !== id)
        return true
      } catch (err) {
        campaignsError.value = formatApiError(err)
        console.error('Failed to delete campaign:', err)
        return false
      } finally {
        campaignsLoading.value = false
      }
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
      refreshSharedLinks,

      // Campaigns
      campaigns,
      campaignsLoading,
      campaignsError,
      fetchCampaigns,
      createCampaign,
      updateCampaign,
      deleteCampaign
    }
  },
  {
    persist: {
      paths: ['pageSize', 'filters', 'sharedLinkFilters'] // Persist user preferences
    }
  }
)
