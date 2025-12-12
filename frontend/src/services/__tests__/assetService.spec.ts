// @ts-nocheck
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { assetService } from '../assetService'
import { apiService } from '../apiService'
import type {
  Asset,
  PaginatedResponse,
  SearchResponse,
  BulkOperationResponse
} from '@/types/api'

// Mock apiService
vi.mock('../apiService', () => ({
  apiService: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    clearCache: vi.fn()
  }
}))

const mockedApiService = vi.mocked(apiService)

describe('AssetService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAssets', () => {
    it('should fetch assets with default params', async () => {
      const mockResponse: PaginatedResponse<Asset> = {
        count: 100,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            label: 'Test Asset',
            filename: 'test.jpg',
            size: 1024,
            mime_type: 'image/jpeg',
            date_added: '2025-11-25T10:00:00Z'
          }
        ]
      }

      mockedApiService.get.mockResolvedValue(mockResponse)

      const result = await assetService.getAssets()

      expect(mockedApiService.get).toHaveBeenCalledWith(
        '/v4/dam/assets/',
        { params: {} },
        true
      )
      expect(result).toEqual(mockResponse)
    })

    it('should fetch assets with pagination params', async () => {
      const mockResponse: PaginatedResponse<Asset> = {
        count: 100,
        next: '/api/v4/dam/assets/?page=2',
        previous: null,
        results: []
      }

      mockedApiService.get.mockResolvedValue(mockResponse)

      const result = await assetService.getAssets({
        page: 2,
        page_size: 50
      })

      expect(mockedApiService.get).toHaveBeenCalledWith(
        '/v4/dam/assets/',
        { params: { page: 2, page_size: 50 } },
        true
      )
      expect(result).toEqual(mockResponse)
    })

    it('should fetch assets with filters', async () => {
      const mockResponse: PaginatedResponse<Asset> = {
        count: 10,
        next: null,
        previous: null,
        results: []
      }

      mockedApiService.get.mockResolvedValue(mockResponse)

      await assetService.getAssets({
        type: 'image',
        tags: 'campaign',
        sort: '-date_added'
      })

      expect(mockedApiService.get).toHaveBeenCalledWith(
        '/v4/dam/assets/',
        {
          params: {
            type: 'image',
            tags: 'campaign',
            sort: '-date_added'
          }
        },
        true
      )
    })
  })

  describe('getAsset', () => {
    it('should fetch single asset by ID', async () => {
      const mockAsset = {
        id: 1,
        label: 'Test Asset',
        filename: 'test.jpg',
        size: 1024,
        mime_type: 'image/jpeg',
        date_added: '2025-11-25T10:00:00Z',
        file_details: {
          filename: 'test.jpg',
          size: 1024,
          mime_type: 'image/jpeg',
          uploaded_date: '2025-11-25T10:00:00Z'
        },
        comments: [],
        version_history: []
      }

      mockedApiService.get.mockResolvedValue(mockAsset)

      const result = await assetService.getAsset(1)

      expect(mockedApiService.get).toHaveBeenCalledWith(
        '/v4/dam/assets/1/',
        undefined,
        true
      )
      expect(result).toEqual(mockAsset)
    })
  })

  describe('searchAssets', () => {
    it('should search assets with query', async () => {
      const mockResponse: SearchResponse = {
        count: 5,
        results: [],
        facets: {
          type: { image: 5 },
          tags: { campaign: 3 }
        }
      }

      mockedApiService.post.mockResolvedValue(mockResponse)

      const result = await assetService.searchAssets({
        q: 'landscape',
        limit: 20
      })

      expect(mockedApiService.post).toHaveBeenCalledWith(
        '/v4/dam/assets/search/',
        { q: 'landscape', limit: 20 },
        undefined
      )
      expect(result).toEqual(mockResponse)
    })

    it('should search assets with filters', async () => {
      const mockResponse: SearchResponse = {
        count: 10,
        results: [],
        facets: {}
      }

      mockedApiService.post.mockResolvedValue(mockResponse)

      await assetService.searchAssets({
        q: 'test',
        filters: {
          type: ['image'],
          tags: ['campaign'],
          date_range: ['2025-01-01', '2025-12-31']
        }
      })

      expect(mockedApiService.post).toHaveBeenCalledWith(
        '/v4/dam/assets/search/',
        {
          q: 'test',
          filters: {
            type: ['image'],
            tags: ['campaign'],
            date_range: ['2025-01-01', '2025-12-31']
          }
        },
        undefined
      )
    })
  })

  describe('bulkOperation', () => {
    it('should perform bulk operation', async () => {
      const mockResponse: BulkOperationResponse = {
        success: true,
        updated: 10,
        failed: 0
      }

      mockedApiService.post.mockResolvedValue(mockResponse)

      const result = await assetService.bulkOperation({
        ids: [1, 2, 3],
        action: 'add_tags',
        data: { tags: ['new-tag'] }
      })

      expect(mockedApiService.post).toHaveBeenCalledWith(
        '/v4/dam/assets/bulk/',
        {
          ids: [1, 2, 3],
          action: 'add_tags',
          data: { tags: ['new-tag'] }
        },
        undefined
      )
      expect(result).toEqual(mockResponse)
    })

    it('should clear cache after successful bulk operation', async () => {
      const mockResponse: BulkOperationResponse = {
        success: true,
        updated: 5,
        failed: 0
      }

      mockedApiService.post.mockResolvedValue(mockResponse)

      await assetService.bulkOperation({
        ids: [1, 2],
        action: 'delete'
      })

      expect(mockedApiService.clearCache).toHaveBeenCalled()
    })
  })

  describe('updateAsset', () => {
    it('should update asset and clear cache', async () => {
      const updateData = { label: 'Updated Label' }
      const mockResponse = {
        id: 1,
        label: 'Updated Label',
        filename: 'test.jpg',
        size: 1024,
        mime_type: 'image/jpeg',
        date_added: '2025-11-25T10:00:00Z',
        file_details: {
          filename: 'test.jpg',
          size: 1024,
          mime_type: 'image/jpeg',
          uploaded_date: '2025-11-25T10:00:00Z'
        },
        comments: [],
        version_history: []
      }

      mockedApiService.put.mockResolvedValue(mockResponse)

      const result = await assetService.updateAsset(1, updateData)

      expect(mockedApiService.put).toHaveBeenCalledWith(
        '/v4/dam/assets/1/',
        updateData,
        undefined
      )
      expect(mockedApiService.clearCache).toHaveBeenCalled()
      expect(result).toEqual(mockResponse)
    })
  })

  describe('deleteAsset', () => {
    it('should delete asset and clear cache', async () => {
      mockedApiService.delete.mockResolvedValue(undefined)

      await assetService.deleteAsset(1)

      expect(mockedApiService.delete).toHaveBeenCalledWith(
        '/v4/dam/assets/1/',
        undefined
      )
      expect(mockedApiService.clearCache).toHaveBeenCalled()
    })
  })

  describe('clearCache', () => {
    it('should clear asset cache', () => {
      assetService.clearCache()
      expect(mockedApiService.clearCache).toHaveBeenCalled()
    })
  })
})
