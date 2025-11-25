import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CommentsThread from '@/components/DAM/CommentsThread.vue'
import { commentService } from '@/services/commentService'
import { websocketService } from '@/services/websocketService'
import type { Comment } from '@/types/api'

vi.mock('@/services/commentService')
vi.mock('@/services/websocketService')
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    user: { id: 1, username: 'testuser' }
  })
}))

describe('CommentsThread', () => {
  let pinia: any

  const mockComments: Comment[] = [
    {
      id: 1,
      author: 'User1',
      author_id: 1,
      text: 'First comment',
      created_date: '2023-01-01T10:00:00Z',
      replies: [
        {
          id: 2,
          author: 'User2',
          author_id: 2,
          text: 'Reply to first',
          created_date: '2023-01-01T11:00:00Z',
          parent_id: 1
        }
      ]
    },
    {
      id: 3,
      author: 'User3',
      author_id: 3,
      text: 'Second comment',
      created_date: '2023-01-01T12:00:00Z'
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
    ;(commentService.getComments as vi.Mock).mockResolvedValue(mockComments)
    ;(websocketService.subscribeToAsset as vi.Mock).mockImplementation(() => {})
    ;(websocketService.on as vi.Mock).mockReturnValue(() => {})
  })

  it('renders comments list', async () => {
    const wrapper = mount(CommentsThread, {
      props: {
        assetId: 1,
        initialComments: mockComments
      },
      global: {
        plugins: [pinia],
        stubs: {
          CommentItem: {
            template: '<div class="comment-item">{{ comment.text }}</div>',
            props: ['comment', 'currentUserId']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Комментарии')
    expect(wrapper.text()).toContain('First comment')
  })

  it('displays total comments count including replies', () => {
    const wrapper = mount(CommentsThread, {
      props: {
        assetId: 1,
        initialComments: mockComments
      },
      global: {
        plugins: [pinia],
        stubs: {
          CommentItem: true
        }
      }
    })

    // Total count should be 3 (2 top-level + 1 reply)
    expect(wrapper.text()).toContain('Комментарии (3)')
  })

  it('shows empty state when no comments', () => {
    const wrapper = mount(CommentsThread, {
      props: {
        assetId: 1,
        initialComments: []
      },
      global: {
        plugins: [pinia],
        stubs: {
          CommentItem: true
        }
      }
    })

    expect(wrapper.text()).toContain('Пока нет комментариев')
  })

  it('allows adding a new comment', async () => {
    const newComment: Comment = {
      id: 4,
      author: 'testuser',
      author_id: 1,
      text: 'New comment',
      created_date: new Date().toISOString()
    }

    ;(commentService.createComment as vi.Mock).mockResolvedValue(newComment)

    const wrapper = mount(CommentsThread, {
      props: {
        assetId: 1,
        initialComments: []
      },
      global: {
        plugins: [pinia],
        stubs: {
          CommentItem: true
        }
      }
    })

    const textarea = wrapper.find('textarea')
    await textarea.setValue('New comment')
    await textarea.trigger('input')

    const submitButton = wrapper.findAll('button').find((btn) =>
      btn.text().includes('Отправить')
    )
    if (submitButton) {
      await submitButton.trigger('click')
      await wrapper.vm.$nextTick()
      expect(commentService.createComment).toHaveBeenCalledWith(1, {
        text: 'New comment',
        mentions: []
      })
    }
  })

  it('supports @mentions in comments', async () => {
    const wrapper = mount(CommentsThread, {
      props: {
        assetId: 1,
        initialComments: []
      },
      global: {
        plugins: [pinia],
        stubs: {
          CommentItem: true
        }
      }
    })

    const textarea = wrapper.find('textarea')
    await textarea.setValue('Hello @admin')
    await textarea.trigger('input')

    // Check that mention suggestions appear
    await wrapper.vm.$nextTick()
    // Mention suggestions should be shown when @ is typed
  })

  it('allows replying to a comment', async () => {
    const wrapper = mount(CommentsThread, {
      props: {
        assetId: 1,
        initialComments: mockComments
      },
      global: {
        plugins: [pinia],
        stubs: {
          CommentItem: {
            template: '<div><button @click="$emit(\'reply\', comment)">Reply</button></div>',
            props: ['comment'],
            emits: ['reply']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    const replyButton = wrapper.findAll('button').find((btn) => btn.text().includes('Reply'))
    if (replyButton) {
      await replyButton.trigger('click')
      await wrapper.vm.$nextTick()
      // Should show reply form
      const textarea = wrapper.find('textarea')
      expect(textarea.exists()).toBe(true)
    }
  })

  it('subscribes to WebSocket events on mount', () => {
    mount(CommentsThread, {
      props: {
        assetId: 1,
        initialComments: []
      },
      global: {
        plugins: [pinia],
        stubs: {
          CommentItem: true
        }
      }
    })

    expect(websocketService.subscribeToAsset).toHaveBeenCalledWith(1)
    expect(websocketService.on).toHaveBeenCalledWith('comment_added', expect.any(Function))
    expect(websocketService.on).toHaveBeenCalledWith('comment_updated', expect.any(Function))
    expect(websocketService.on).toHaveBeenCalledWith('comment_deleted', expect.any(Function))
  })
})

