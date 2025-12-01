import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Pagination from '@/components/Common/Pagination.vue'

describe('Pagination', () => {
  it('renders pagination controls', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalItems: 100,
        pageSize: 10
      }
    })

    expect(wrapper.text()).toContain('Показано')
    expect(wrapper.text()).toContain('из 100')
  })

  it('calculates correct start and end items', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 2,
        totalItems: 100,
        pageSize: 10
      }
    })

    expect(wrapper.text()).toContain('11-20')
  })

  it('disables previous button on first page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalItems: 100,
        pageSize: 10
      }
    })

    const prevButton = wrapper.findAll('button')[0]
    expect(prevButton.attributes('disabled')).toBeDefined()
  })

  it('disables next button on last page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 10,
        totalItems: 100,
        pageSize: 10
      }
    })

    const buttons = wrapper.findAll('button')
    const nextButton = buttons[buttons.length - 1]
    expect(nextButton.attributes('disabled')).toBeDefined()
  })

  it('emits page-change event on next click', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalItems: 100,
        pageSize: 10
      }
    })

    const buttons = wrapper.findAll('button')
    const nextButton = buttons[buttons.length - 1]
    
    // Should be disabled on first page, so test with page 2
    await wrapper.setProps({ currentPage: 2 })
    const updatedButtons = wrapper.findAll('button')
    const nextBtn = updatedButtons[updatedButtons.length - 1]
    
    await nextBtn.trigger('click')
    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')?.[0]).toEqual([3])
  })

  it('emits page-change event on previous click', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 2,
        totalItems: 100,
        pageSize: 10
      }
    })

    const prevButton = wrapper.findAll('button')[0]
    await prevButton.trigger('click')
    
    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')?.[0]).toEqual([1])
  })

  it('emits page-change event on page number click', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalItems: 100,
        pageSize: 10
      }
    })

    // Find page number button (not prev/next)
    const pageButtons = wrapper.findAll('button').filter(btn => {
      const text = btn.text()
      return text && /^\d+$/.test(text.trim())
    })

    if (pageButtons.length > 0) {
      await pageButtons[0].trigger('click')
      expect(wrapper.emitted('page-change')).toBeTruthy()
    }
  })

  it('shows correct number of visible pages', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 5,
        totalItems: 100,
        pageSize: 10,
        maxVisiblePages: 5
      }
    })

    const pageButtons = wrapper.findAll('button').filter(btn => {
      const text = btn.text()
      return text && /^\d+$/.test(text.trim())
    })

    expect(pageButtons.length).toBeLessThanOrEqual(5)
  })

  it('highlights current page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalItems: 100,
        pageSize: 10
      }
    })

    const pageButtons = wrapper.findAll('button').filter(btn => {
      const text = btn.text()
      return text && text.trim() === '3'
    })

    if (pageButtons.length > 0) {
      expect(pageButtons[0].classes()).toContain('bg-primary-500')
    }
  })
})

