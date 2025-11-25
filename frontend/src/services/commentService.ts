import { apiService } from './apiService'
import type {
  Comment,
  CreateCommentRequest,
  UpdateCommentRequest,
  PaginatedResponse
} from '@/types/api'

class CommentService {
  /**
   * Get comments for an asset
   */
  async getComments(assetId: number): Promise<Comment[]> {
    const response = await apiService.get<PaginatedResponse<Comment>>(
      `/v4/dam/assets/${assetId}/comments/`
    )
    return response.results || []
  }

  /**
   * Create a new comment
   */
  async createComment(
    assetId: number,
    comment: CreateCommentRequest
  ): Promise<Comment> {
    return apiService.post<Comment>(
      `/v4/dam/assets/${assetId}/comments/`,
      comment
    )
  }

  /**
   * Update an existing comment
   */
  async updateComment(
    assetId: number,
    commentId: number,
    comment: UpdateCommentRequest
  ): Promise<Comment> {
    return apiService.put<Comment>(
      `/v4/dam/assets/${assetId}/comments/${commentId}/`,
      comment
    )
  }

  /**
   * Delete a comment
   */
  async deleteComment(assetId: number, commentId: number): Promise<void> {
    return apiService.delete<void>(
      `/v4/dam/assets/${assetId}/comments/${commentId}/`
    )
  }

  /**
   * Create a reply to a comment
   */
  async createReply(
    assetId: number,
    parentId: number,
    comment: CreateCommentRequest
  ): Promise<Comment> {
    return apiService.post<Comment>(
      `/v4/dam/assets/${assetId}/comments/`,
      {
        ...comment,
        parent_id: parentId
      }
    )
  }
}

export const commentService = new CommentService()

