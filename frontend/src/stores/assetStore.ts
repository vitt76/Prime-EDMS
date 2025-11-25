import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { assetService } from '@/services/assetService'
import type { Asset, GetAssetsParams, PaginatedResponse } from '@/types/api'
import { formatApiError } from '@/utils/errors'

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

    // Actions
    async function fetchAssets(params?: GetAssetsParams) {
      isLoading.value = true
      error.value = null

      try {
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
      refresh
    }
  },
  {
    persist: {
      paths: ['pageSize', 'sortBy', 'filters'] // Persist user preferences
    }
  }
)

