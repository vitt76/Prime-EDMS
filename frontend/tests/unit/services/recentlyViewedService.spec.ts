import { describe, it, expect, beforeEach, vi } from 'vitest'
import { getRecentlyViewed } from '@/services/recentlyViewedService'
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

describe('recentlyViewedService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('calls GET headless documents recently-viewed with default params', async () => {
    ;(apiService.get as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { results: [], count: 0 }
    })

    await getRecentlyViewed()

    expect(apiService.get).toHaveBeenCalledWith(
      '/api/v4/headless/documents/recently-viewed/',
      { params: { limit: 20, days: 30 } }
    )
  })

  it('passes limit and days params', async () => {
    ;(apiService.get as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { results: [], count: 0 }
    })

    await getRecentlyViewed({ limit: 10, days: 7 })

    expect(apiService.get).toHaveBeenCalledWith(
      '/api/v4/headless/documents/recently-viewed/',
      { params: { limit: 10, days: 7 } }
    )
  })

  it('returns adapted results and count', async () => {
    ;(apiService.get as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: {
        results: [
          { id: 1, label: 'Doc 1' },
          { id: 2, label: 'Doc 2' }
        ],
        count: 2
      }
    })

    const res = await getRecentlyViewed({ limit: 20 })

    expect(res.results).toHaveLength(2)
    expect(res.results[0].id).toBe(1)
    expect(res.results[0].label).toBe('Doc 1')
    expect(res.count).toBe(2)
  })
})
