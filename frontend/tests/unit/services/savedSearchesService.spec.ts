import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  listSavedSearches,
  createSavedSearch,
  updateSavedSearch,
  deleteSavedSearch,
  runSavedSearch
} from '@/services/savedSearchesService'
import { apiService } from '@/services/apiService'

vi.mock('@/services/apiService')
vi.mock('@/services/adapters/mayanAdapter', () => ({
  adaptBackendAsset: (doc: { id: number; label: string }) => ({
    id: doc.id,
    label: doc.label,
    filename: String(doc.id),
    size: 0,
    mime_type: 'image/jpeg',
    date_added: new Date().toISOString()
  })
}))

describe('savedSearchesService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('listSavedSearches calls GET and returns array', async () => {
    const list = [
      { id: 1, name: 'Test', query: 'q', filters: {}, created_at: '2024-01-01T00:00:00Z' }
    ]
    ;(apiService.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: list })

    const result = await listSavedSearches()

    expect(apiService.get).toHaveBeenCalledWith('/api/v4/headless/saved-searches/')
    expect(result).toEqual(list)
  })

  it('createSavedSearch sends name, query, filters', async () => {
    const created = {
      id: 1,
      name: 'My search',
      query: 'test',
      filters: { orientation: 'landscape' },
      created_at: '2024-01-01T00:00:00Z'
    }
    ;(apiService.post as ReturnType<typeof vi.fn>).mockResolvedValue({ data: created })

    const result = await createSavedSearch({
      name: 'My search',
      query: 'test',
      filters: { orientation: 'landscape' }
    })

    expect(apiService.post).toHaveBeenCalledWith('/api/v4/headless/saved-searches/', {
      name: 'My search',
      query: 'test',
      filters: { orientation: 'landscape' }
    })
    expect(result).toEqual(created)
  })

  it('updateSavedSearch sends PATCH with name', async () => {
    const updated = {
      id: 1,
      name: 'New name',
      query: '',
      filters: {},
      created_at: '2024-01-01T00:00:00Z'
    }
    ;(apiService.patch as ReturnType<typeof vi.fn>).mockResolvedValue({ data: updated })

    await updateSavedSearch(1, { name: 'New name' })

    expect(apiService.patch).toHaveBeenCalledWith(
      '/api/v4/headless/saved-searches/1/',
      { name: 'New name' }
    )
  })

  it('deleteSavedSearch calls DELETE', async () => {
    ;(apiService.delete as ReturnType<typeof vi.fn>).mockResolvedValue(undefined)

    await deleteSavedSearch(1)

    expect(apiService.delete).toHaveBeenCalledWith('/api/v4/headless/saved-searches/1/')
  })

  it('runSavedSearch calls GET run/ with page_size and returns adapted results', async () => {
    ;(apiService.get as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: {
        results: [{ id: 10, label: 'Doc' }],
        count: 1
      }
    })

    const result = await runSavedSearch(1, 50)

    expect(apiService.get).toHaveBeenCalledWith(
      '/api/v4/headless/saved-searches/1/run/',
      { params: { page_size: 50 } }
    )
    expect(result.results).toHaveLength(1)
    expect(result.results[0].id).toBe(10)
    expect(result.count).toBe(1)
  })
})
