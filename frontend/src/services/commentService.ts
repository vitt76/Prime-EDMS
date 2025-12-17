import { apiService } from './apiService'
import type {
  Comment,
  CreateCommentRequest,
  UpdateCommentRequest
} from '@/types/api'
import {
  adaptMayanCommentToFrontend,
  adaptFrontendCommentToMayan,
  type MayanCommentResponse
} from '@/services/adapters/mayanCommentAdapter'

class CommentService {
  /**
   * Get comments for a document
   * @param documentId - Mayan EDMS document ID
   */
  async getComments(documentId: number): Promise<Comment[]> {
    try {
      const response = await apiService.get<MayanCommentResponse[] | { results: MayanCommentResponse[] }>(
        `/api/v4/documents/${documentId}/comments/`,
        undefined,
        false // Don't cache comments
      )
      
      // Handle both paginated and non-paginated responses
      let comments: MayanCommentResponse[] = []
      if (Array.isArray(response)) {
        comments = response
      } else if (response && typeof response === 'object' && 'results' in response) {
        comments = (response as { results: MayanCommentResponse[] }).results || []
      }
      
      return comments.map(adaptMayanCommentToFrontend)
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.error('[CommentService] Failed to get comments:', {
          documentId,
          error: err,
          status: err?.response?.status,
          data: err?.response?.data
        })
      }
      throw err
    }
  }

  /**
   * Create a new comment
   * @param documentId - Mayan EDMS document ID
   * @param text - Comment text
   */
  async createComment(documentId: number, text: string): Promise<Comment> {
    try {
      const mayanRequest = adaptFrontendCommentToMayan(text)
      const response = await apiService.post<MayanCommentResponse>(
        `/api/v4/documents/${documentId}/comments/`,
        mayanRequest
      )
      return adaptMayanCommentToFrontend(response)
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.error('[CommentService] Failed to create comment:', {
          documentId,
          error: err,
          status: err?.response?.status,
          data: err?.response?.data
        })
      }
      throw err
    }
  }

  /**
   * Update an existing comment
   * @param documentId - Mayan EDMS document ID
   * @param commentId - Comment ID
   * @param text - Updated comment text
   */
  async updateComment(
    documentId: number,
    commentId: number,
    text: string
  ): Promise<Comment> {
    try {
      const mayanRequest = adaptFrontendCommentToMayan(text)
      const response = await apiService.patch<MayanCommentResponse>(
        `/api/v4/documents/${documentId}/comments/${commentId}/`,
        mayanRequest
      )
      return adaptMayanCommentToFrontend(response)
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.error('[CommentService] Failed to update comment:', {
          documentId,
          commentId,
          error: err,
          status: err?.response?.status,
          data: err?.response?.data
        })
      }
      throw err
    }
  }

  /**
   * Delete a comment
   * @param documentId - Mayan EDMS document ID
   * @param commentId - Comment ID
   */
  async deleteComment(documentId: number, commentId: number): Promise<void> {
    try {
      await apiService.delete<void>(
        `/api/v4/documents/${documentId}/comments/${commentId}/`
      )
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.error('[CommentService] Failed to delete comment:', {
          documentId,
          commentId,
          error: err,
          status: err?.response?.status,
          data: err?.response?.data
        })
      }
      throw err
    }
  }
}

export const commentService = new CommentService()

