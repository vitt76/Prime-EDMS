import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { assetService } from '@/services/assetService'
import type { Asset, GetAssetsParams, PaginatedResponse } from '@/types/api'
import { formatApiError } from '@/utils/errors'
import type { AxiosProgressEvent } from 'axios'

interface UploadOptions {
  onUploadProgress?: (event: AxiosProgressEvent) => void
  signal?: AbortSignal
}
export const useAssetStore = defineStore(
  'asset',
  () => {
    // State
    const assets = ref<Asset[]>([])
    const totalCount = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(50)
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const selectedAssets = ref<Asset[]>([])
    const currentAsset = ref<Asset | null>(null)
    const sortBy = ref<string>('-date_added')
    const filters = ref<GetAssetsParams>({})

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

    const selectedCount = computed(() => selectedAssets.value.length)

    const currentPageAssets = computed(() => assets.value)

    // Mock assets for dev mode
    const mockAssets: Asset[] = [
      { id: 1, label: 'image_001.jpg', file_type: 'image', mime_type: 'image/jpeg', size: 2500000, date_added: new Date().toISOString(), thumbnail_url: '' },
      { id: 2, label: 'video_promo.mp4', file_type: 'video', mime_type: 'video/mp4', size: 15000000, date_added: new Date(Date.now() - 86400000).toISOString(), thumbnail_url: '' },
      { id: 3, label: 'report_2025.pdf', file_type: 'document', mime_type: 'application/pdf', size: 500000, date_added: new Date(Date.now() - 172800000).toISOString(), thumbnail_url: '' },
      { id: 4, label: 'photo_landscape.png', file_type: 'image', mime_type: 'image/png', size: 3200000, date_added: new Date(Date.now() - 259200000).toISOString(), thumbnail_url: '' },
      { id: 5, label: 'presentation.pptx', file_type: 'document', mime_type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation', size: 8000000, date_added: new Date(Date.now() - 345600000).toISOString(), thumbnail_url: '' },
    ] as Asset[]

    // Actions
    async function fetchAssets(params?: GetAssetsParams) {
      isLoading.value = true
      error.value = null

      try {
        // In dev mode, use mock data
        if (import.meta.env.DEV) {
          await new Promise(resolve => setTimeout(resolve, 300))
          assets.value = mockAssets
          totalCount.value = mockAssets.length
          return
        }

        const queryParams: GetAssetsParams = {
          page: currentPage.value,
          page_size: pageSize.value,
          sort: sortBy.value,
          ...filters.value,
          ...params
        }

        const response: PaginatedResponse<Asset> = await assetService.getAssets(
          queryParams
        )

        assets.value = response.results
        totalCount.value = response.count

        // Update current page if provided
        if (params?.page) {
          currentPage.value = params.page
        }
      } catch (err) {
        // In dev mode, fallback to mock data
        if (import.meta.env.DEV) {
          console.warn('[Dev] Using mock assets')
          assets.value = mockAssets
          totalCount.value = mockAssets.length
          return
        }
        error.value = formatApiError(err)
        assets.value = []
        totalCount.value = 0
        throw err
      } finally {
        isLoading.value = false
      }
    }

    async function getAssetDetail(id: number) {
      isLoading.value = true
      error.value = null

      try {
        const asset = await assetService.getAsset(id)
        currentAsset.value = asset
        return asset
      } catch (err) {
        error.value = formatApiError(err)
        currentAsset.value = null
        throw err
      } finally {
        isLoading.value = false
      }
    }

    function nextPage() {
      if (hasNextPage.value) {
        currentPage.value++
        fetchAssets()
      }
    }

    function previousPage() {
      if (hasPreviousPage.value) {
        currentPage.value--
        fetchAssets()
      }
    }

    function setPage(page: number) {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        fetchAssets()
      }
    }

    function setPageSize(size: number) {
      pageSize.value = Math.min(Math.max(size, 1), 100) // Clamp between 1 and 100
      currentPage.value = 1 // Reset to first page
      fetchAssets()
    }

    function selectAsset(asset: Asset, multiSelect = false) {
      const index = selectedAssets.value.findIndex((a) => a.id === asset.id)

      if (index === -1) {
        if (multiSelect) {
          selectedAssets.value.push(asset)
        } else {
          selectedAssets.value = [asset]
        }
      } else {
        selectedAssets.value.splice(index, 1)
      }
    }

    function selectAll() {
      selectedAssets.value = [...assets.value]
    }

    function clearSelection() {
      selectedAssets.value = []
    }

    function setSortBy(sort: string) {
      sortBy.value = sort
      currentPage.value = 1
      fetchAssets()
    }

    function applyFilters(newFilters: GetAssetsParams) {
      filters.value = { ...filters.value, ...newFilters }
      currentPage.value = 1
      fetchAssets()
    }

    function clearFilters() {
      filters.value = {}
      currentPage.value = 1
      fetchAssets()
    }

    function refresh() {
      fetchAssets()
    }

    // Initialize - fetch first page on store creation (optional)
    // fetchAssets() // Uncomment if you want auto-fetch on store init

    async function uploadAsset(
      formData: FormData,
      options?: UploadOptions
    ): Promise<Asset> {
      return assetService.uploadAsset(formData, {
        onUploadProgress: options?.onUploadProgress,
        signal: options?.signal
      })
    }

    return {
      // State
      assets,
      totalCount,
      currentPage,
      pageSize,
      isLoading,
      error,
      selectedAssets,
      currentAsset,
      sortBy,
      filters,

      // Getters
      hasNextPage,
      hasPreviousPage,
      totalPages,
      selectedCount,
      currentPageAssets,

      // Actions
      fetchAssets,
      getAssetDetail,
      nextPage,
      previousPage,
      setPage,
      setPageSize,
      selectAsset,
      selectAll,
      clearSelection,
      setSortBy,
      applyFilters,
      clearFilters,
      refresh,
      uploadAsset
    }
  },
  {
    persist: {
      paths: ['pageSize', 'sortBy', 'filters'] // Persist user preferences
    }
  }
)

