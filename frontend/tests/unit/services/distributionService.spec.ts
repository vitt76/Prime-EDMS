import { describe, it, expect, beforeEach, vi } from 'vitest'
import { distributionService } from '@/services/distributionService'
import { apiService } from '@/services/apiService'
import type { Publication, CreatePublicationRequest, UpdatePublicationRequest } from '@/types/api'

vi.mock('@/services/apiService')

describe('distributionService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('gets paginated list of publications', async () => {
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

    const mockResponse = {
      results: mockPublications,
      count: 1,
      next: null,
      previous: null
    }

    ;(apiService.get as vi.Mock).mockResolvedValue(mockResponse)

    const response = await distributionService.getPublications({ page: 1 })

    expect(apiService.get).toHaveBeenCalledWith(
      '/v4/distribution/publications/',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
      false
    )
    expect(response.results).toEqual(mockPublications)
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

    const request: CreatePublicationRequest = {
      title: 'New Publication',
      asset_ids: [1, 2],
      channel_ids: [1]
    }

    ;(apiService.post as vi.Mock).mockResolvedValue(newPublication)

    const result = await distributionService.createPublication(request)

    expect(apiService.post).toHaveBeenCalledWith('/v4/distribution/publications/', request)
    expect(result).toEqual(newPublication)
  })

  it('updates a publication', async () => {
    const updated: Publication = {
      id: 1,
      title: 'Updated Publication',
      status: 'published',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T12:00:00Z',
      created_by: 'User1',
      created_by_id: 1,
      assets: [],
      channels: []
    }

    const request: UpdatePublicationRequest = {
      title: 'Updated Publication'
    }

    ;(apiService.put as vi.Mock).mockResolvedValue(updated)

    const result = await distributionService.updatePublication(1, request)

    expect(apiService.put).toHaveBeenCalledWith('/v4/distribution/publications/1/', request)
    expect(result).toEqual(updated)
  })

  it('deletes a publication', async () => {
    ;(apiService.delete as vi.Mock).mockResolvedValue(undefined)

    await distributionService.deletePublication(1)

    expect(apiService.delete).toHaveBeenCalledWith('/v4/distribution/publications/1/')
  })

  it('publishes a publication', async () => {
    const published: Publication = {
      id: 1,
      title: 'Publication',
      status: 'published',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T12:00:00Z',
      published_date: '2023-01-01T12:00:00Z',
      created_by: 'User1',
      created_by_id: 1,
      assets: [],
      channels: []
    }

    ;(apiService.post as vi.Mock).mockResolvedValue(published)

    const result = await distributionService.publishPublication(1)

    expect(apiService.post).toHaveBeenCalledWith('/v4/distribution/publications/1/publish/')
    expect(result).toEqual(published)
  })

  it('gets available channels', async () => {
    const mockChannels = [
      {
        id: 1,
        name: 'Website',
        type: 'website',
        status: 'active'
      }
    ]

    const mockResponse = {
      results: mockChannels,
      count: 1
    }

    ;(apiService.get as vi.Mock).mockResolvedValue(mockResponse)

    const channels = await distributionService.getChannels()

    expect(apiService.get).toHaveBeenCalledWith('/v4/distribution/channels/')
    expect(channels).toEqual(mockChannels)
  })
})

