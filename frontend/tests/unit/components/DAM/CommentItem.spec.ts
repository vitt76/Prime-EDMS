import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CommentItem from '@/components/DAM/CommentItem.vue'
import type { Comment } from '@/types/api'

describe('CommentItem', () => {
  let pinia: any

  const mockComment: Comment = {
    id: 1,
    author: 'Test User',
    author_id: 1,
    text: 'This is a test comment with @mention',
    created_date: '2023-01-01T10:00:00Z'
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('renders comment text', () => {
    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('This is a test comment')
    expect(wrapper.text()).toContain('Test User')
  })

  it('displays author avatar or initial', () => {
    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    // Should show avatar or initial
    const avatar = wrapper.find('.w-10.h-10')
    expect(avatar.exists()).toBe(true)
  })

  it('highlights @mentions in text', () => {
    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    // Mentions should be highlighted
    const mentions = wrapper.findAll('.text-primary-500')
    expect(mentions.length).toBeGreaterThan(0)
  })

  it('shows edit and delete buttons for own comments', () => {
    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 1 // Same as comment author_id
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('Редактировать')
    expect(wrapper.text()).toContain('Удалить')
  })

  it('hides edit and delete buttons for other users comments', () => {
    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 2 // Different from comment author_id
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).not.toContain('Редактировать')
    expect(wrapper.text()).not.toContain('Удалить')
  })

  it('allows editing comment', async () => {
    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    const editButton = wrapper.findAll('button').find((btn) =>
      btn.text().includes('Редактировать')
    )
    if (editButton) {
      await editButton.trigger('click')
      await wrapper.vm.$nextTick()

      const textarea = wrapper.find('textarea')
      expect(textarea.exists()).toBe(true)
      expect(textarea.element.value).toBe(mockComment.text)
    }
  })

  it('emits edit event when saving edited comment', async () => {
    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    // Start editing
    await wrapper.vm.startEdit()
    await wrapper.vm.$nextTick()

    // Change text
    wrapper.vm.editText = 'Updated comment'
    await wrapper.vm.$nextTick()

    // Save
    await wrapper.vm.saveEdit()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')?.[0][0]).toBe(mockComment)
    expect(wrapper.emitted('edit')?.[0][1]).toBe('Updated comment')
  })

  it('emits reply event when reply button is clicked', async () => {
    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    const replyButton = wrapper.findAll('button').find((btn) =>
      btn.text().includes('Ответить')
    )
    if (replyButton) {
      await replyButton.trigger('click')
      expect(wrapper.emitted('reply')).toBeTruthy()
      expect(wrapper.emitted('reply')?.[0][0]).toBe(mockComment)
    }
  })

  it('emits delete event when delete button is clicked', async () => {
    window.confirm = vi.fn(() => true)

    const wrapper = mount(CommentItem, {
      props: {
        comment: mockComment,
        currentUserId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    const deleteButton = wrapper.findAll('button').find((btn) =>
      btn.text().includes('Удалить')
    )
    if (deleteButton) {
      await deleteButton.trigger('click')
      expect(wrapper.emitted('delete')).toBeTruthy()
      expect(wrapper.emitted('delete')?.[0][0]).toBe(mockComment)
    }
  })

  it('displays nested replies', () => {
    const commentWithReplies: Comment = {
      ...mockComment,
      replies: [
        {
          id: 2,
          author: 'User2',
          author_id: 2,
          text: 'Reply comment',
          created_date: '2023-01-01T11:00:00Z',
          parent_id: 1
        }
      ]
    }

    const wrapper = mount(CommentItem, {
      props: {
        comment: commentWithReplies,
        currentUserId: 1
      },
      global: {
        plugins: [pinia],
        stubs: {
          CommentItem: {
            template: '<div class="reply">{{ comment.text }}</div>',
            props: ['comment', 'currentUserId']
          }
        }
      }
    })

    expect(wrapper.text()).toContain('Reply comment')
  })

  it('shows edited indicator when comment was edited', () => {
    const editedComment: Comment = {
      ...mockComment,
      edited: true,
      updated_date: '2023-01-01T11:00:00Z'
    }

    const wrapper = mount(CommentItem, {
      props: {
        comment: editedComment,
        currentUserId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('отредактировано')
  })
})

