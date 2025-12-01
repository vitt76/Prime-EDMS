import { describe, it, expect, beforeEach, vi } from 'vitest'
import { commentService } from '@/services/commentService'
import { apiService } from '@/services/apiService'
import type { Comment, CreateCommentRequest, UpdateCommentRequest } from '@/types/api'

vi.mock('@/services/apiService')

describe('commentService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('gets comments for an asset', async () => {
    const mockComments: Comment[] = [
      {
        id: 1,
        author: 'User1',
        text: 'Comment 1',
        created_date: '2023-01-01T10:00:00Z'
      }
    ]

    const mockResponse = {
      results: mockComments,
      count: 1
    }

    ;(apiService.get as vi.Mock).mockResolvedValue(mockResponse)

    const comments = await commentService.getComments(1)

    expect(apiService.get).toHaveBeenCalledWith('/v4/dam/assets/1/comments/')
    expect(comments).toEqual(mockComments)
  })

  it('creates a new comment', async () => {
    const newComment: Comment = {
      id: 1,
      author: 'User1',
      text: 'New comment',
      created_date: '2023-01-01T10:00:00Z'
    }

    const request: CreateCommentRequest = {
      text: 'New comment'
    }

    ;(apiService.post as vi.Mock).mockResolvedValue(newComment)

    const result = await commentService.createComment(1, request)

    expect(apiService.post).toHaveBeenCalledWith('/v4/dam/assets/1/comments/', request)
    expect(result).toEqual(newComment)
  })

  it('creates a reply to a comment', async () => {
    const reply: Comment = {
      id: 2,
      author: 'User2',
      text: 'Reply',
      created_date: '2023-01-01T11:00:00Z',
      parent_id: 1
    }

    const request: CreateCommentRequest = {
      text: 'Reply',
      parent_id: 1
    }

    ;(apiService.post as vi.Mock).mockResolvedValue(reply)

    const result = await commentService.createReply(1, 1, { text: 'Reply' })

    expect(apiService.post).toHaveBeenCalledWith('/v4/dam/assets/1/comments/', request)
    expect(result).toEqual(reply)
  })

  it('updates a comment', async () => {
    const updated: Comment = {
      id: 1,
      author: 'User1',
      text: 'Updated comment',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T12:00:00Z',
      edited: true
    }

    const request: UpdateCommentRequest = {
      text: 'Updated comment'
    }

    ;(apiService.put as vi.Mock).mockResolvedValue(updated)

    const result = await commentService.updateComment(1, 1, request)

    expect(apiService.put).toHaveBeenCalledWith('/v4/dam/assets/1/comments/1/', request)
    expect(result).toEqual(updated)
  })

  it('deletes a comment', async () => {
    ;(apiService.delete as vi.Mock).mockResolvedValue(undefined)

    await commentService.deleteComment(1, 1)

    expect(apiService.delete).toHaveBeenCalledWith('/v4/dam/assets/1/comments/1/')
  })
})

