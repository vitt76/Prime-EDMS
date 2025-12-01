import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useDistributionStore } from '@/stores/distributionStore'
import { distributionService } from '@/services/distributionService'
import type { Publication, PaginatedResponse } from '@/types/api'

vi.mock('@/services/distributionService')

describe('distributionStore', () => {
  let store: ReturnType<typeof useDistributionStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useDistributionStore()
    vi.clearAllMocks()
  })

  it('initializes with empty state', () => {
    expect(store.publications).toEqual([])
    expect(store.totalCount).toBe(0)
    expect(store.currentPage).toBe(1)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetches publications and updates state', async () => {
    const mockPublications: Publication[] = [
      {
        id: 1,
        title: 'Publication 1',
        status: 'published',
        created_date: '2023-01-01T10:00:00Z',
        updated_date: '2023-01-01T10:00:00Z',
        created_by: 'User1',
        created_by_id: 1,
        assets: [],
        channels: []
      }
    ]

    const mockResponse: PaginatedResponse<Publication> = {
      count: 1,
      results: mockPublications,
      next: null,
      previous: null
    }

    ;(distributionService.getPublications as vi.Mock).mockResolvedValue(mockResponse)

    await store.fetchPublications()

    expect(store.publications).toEqual(mockPublications)
    expect(store.totalCount).toBe(1)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('handles API errors', async () => {
    const errorMessage = 'Network Error'
    ;(distributionService.getPublications as vi.Mock).mockRejectedValue(new Error(errorMessage))

    await expect(store.fetchPublications()).rejects.toThrow()

    expect(store.error).toBeTruthy()
    expect(store.publications).toEqual([])
    expect(store.totalCount).toBe(0)
  })

  it('creates a new publication', async () => {
    const newPublication: Publication = {
      id: 1,
      title: 'New Publication',
      status: 'draft',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T10:00:00Z',
      created_by: 'User1',
      created_by_id: 1,
      assets: [],
      channels: []
    }

    ;(distributionService.createPublication as vi.Mock).mockResolvedValue(newPublication)

    const result = await store.createPublication({
      title: 'New Publication',
      asset_ids: [],
      channel_ids: []
    })

    expect(store.publications).toContain(newPublication)
    expect(store.totalCount).toBe(1)
    expect(result).toEqual(newPublication)
  })

  it('updates a publication', async () => {
    const existing: Publication = {
      id: 1,
      title: 'Original',
      status: 'draft',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T10:00:00Z',
      created_by: 'User1',
      created_by_id: 1,
      assets: [],
      channels: []
    }

    store.publications = [existing]

    const updated: Publication = {
      ...existing,
      title: 'Updated',
      updated_date: '2023-01-01T12:00:00Z'
    }

    ;(distributionService.updatePublication as vi.Mock).mockResolvedValue(updated)

    const result = await store.updatePublication(1, { title: 'Updated' })

    expect(store.publications[0].title).toBe('Updated')
    expect(result).toEqual(updated)
  })

  it('deletes a publication', async () => {
    const publication: Publication = {
      id: 1,
      title: 'To Delete',
      status: 'draft',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T10:00:00Z',
      created_by: 'User1',
      created_by_id: 1,
      assets: [],
      channels: []
    }

    store.publications = [publication]
    store.totalCount = 1

    ;(distributionService.deletePublication as vi.Mock).mockResolvedValue(undefined)

    await store.deletePublication(1)

    expect(store.publications).not.toContain(publication)
    expect(store.totalCount).toBe(0)
  })

  it('publishes a publication', async () => {
    const draft: Publication = {
      id: 1,
      title: 'Draft',
      status: 'draft',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T10:00:00Z',
      created_by: 'User1',
      created_by_id: 1,
      assets: [],
      channels: []
    }

    store.publications = [draft]

    const published: Publication = {
      ...draft,
      status: 'published',
      published_date: '2023-01-01T12:00:00Z'
    }

    ;(distributionService.publishPublication as vi.Mock).mockResolvedValue(published)

    const result = await store.publishPublication(1)

    expect(store.publications[0].status).toBe('published')
    expect(result).toEqual(published)
  })

  it('applies filters correctly', async () => {
    const mockResponse: PaginatedResponse<Publication> = {
      count: 0,
      results: [],
      next: null,
      previous: null
    }

    ;(distributionService.getPublications as vi.Mock).mockResolvedValue(mockResponse)

    store.applyFilters({ status: 'published' })

    expect(store.filters.status).toBe('published')
    expect(distributionService.getPublications).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'published' })
    )
  })

  it('calculates pagination correctly', () => {
    store.totalCount = 100
    store.pageSize = 20

    expect(store.totalPages).toBe(5)
    expect(store.hasNextPage).toBe(true)
    expect(store.hasPreviousPage).toBe(false)

    store.currentPage = 5
    expect(store.hasNextPage).toBe(false)
    expect(store.hasPreviousPage).toBe(true)
  })
})

