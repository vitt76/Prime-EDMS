/**
 * Trash Service
 * 
 * Handles API interactions for trashed documents:
 * - List trashed documents
 * - Restore documents
 * - Delete documents permanently
 * - Empty trash
 */

import { apiService } from './apiService'
import type { PaginatedResponse } from '@/types/api'

export interface TrashedDocument {
  id: number
  label: string
  document_type: {
    id: number
    label: string
  }
  trashed_date_time: string
  in_trash: boolean
  // Additional fields from serializer
  url?: string
  image_url?: string
}

class TrashService {
  /**
   * Get list of trashed documents
   */
  async getTrashedDocuments(params?: {
    page?: number
    page_size?: number
    ordering?: string
  }): Promise<PaginatedResponse<TrashedDocument>> {
    const response = await apiService.get<PaginatedResponse<TrashedDocument>>(
      '/api/v4/trashed_documents/',
      { params }
    )
    return response
  }

  /**
   * Restore a trashed document
   */
  async restoreDocument(documentId: number): Promise<void> {
    await apiService.post(
      `/api/v4/trashed_documents/${documentId}/restore/`
    )
  }

  /**
   * Restore multiple trashed documents
   */
  async restoreDocuments(documentIds: number[]): Promise<void> {
    await Promise.all(
      documentIds.map(id => this.restoreDocument(id))
    )
  }

  /**
   * Delete a trashed document permanently
   */
  async deleteDocument(documentId: number): Promise<void> {
    await apiService.delete(
      `/api/v4/trashed_documents/${documentId}/`
    )
  }

  /**
   * Delete multiple trashed documents permanently
   */
  async deleteDocuments(documentIds: number[]): Promise<void> {
    await Promise.all(
      documentIds.map(id => this.deleteDocument(id))
    )
  }

  /**
   * Empty trash (delete all trashed documents)
   * Note: Mayan EDMS doesn't have a direct API endpoint for emptying trash,
   * so we delete all documents individually
   */
  async emptyTrash(): Promise<void> {
    // Get all trashed documents
    const response = await this.getTrashedDocuments({ page_size: 1000 })
    const documentIds = response.results.map(doc => doc.id)
    
    // Delete all documents
    if (documentIds.length > 0) {
      await this.deleteDocuments(documentIds)
    }
  }

  /**
   * Get trashed document image/thumbnail
   */
  getDocumentImageUrl(documentId: number): string {
    const baseUrl = import.meta.env.VITE_API_URL || window.location.origin
    return `${baseUrl}/api/v4/trashed_documents/${documentId}/image/`
  }
}

export const trashService = new TrashService()

