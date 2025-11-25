import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MainContent from '@/components/Layout/MainContent.vue'
import { useUiStore } from '@/stores/uiStore'

describe('MainContent', () => {
  let pinia: ReturnType<typeof createPinia>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('renders main content with slot', () => {
    const wrapper = mount(MainContent, {
      global: {
        plugins: [pinia]
      },
      slots: {
        default: '<div>Test Content</div>'
      }
    })

    expect(wrapper.text()).toContain('Test Content')
  })

  it('applies expanded margin when sidebar is expanded', () => {
    const wrapper = mount(MainContent, {
      global: {
        plugins: [pinia]
      }
    })

    const uiStore = useUiStore()
    uiStore.sidebarExpanded = true
    wrapper.vm.$forceUpdate()

    const main = wrapper.find('main')
    expect(main.classes()).toContain('ml-70')
  })

  it('applies collapsed margin when sidebar is collapsed', () => {
    const wrapper = mount(MainContent, {
      global: {
        plugins: [pinia]
      }
    })

    const uiStore = useUiStore()
    uiStore.sidebarExpanded = false
    wrapper.vm.$forceUpdate()

    const main = wrapper.find('main')
    expect(main.classes()).toContain('ml-16')
  })

  it('has correct top margin for header', () => {
    const wrapper = mount(MainContent, {
      global: {
        plugins: [pinia]
      }
    })

    const main = wrapper.find('main')
    expect(main.classes()).toContain('mt-16')
  })

  it('has minimum height for content area', () => {
    const wrapper = mount(MainContent, {
      global: {
        plugins: [pinia]
      }
    })

    const main = wrapper.find('main')
    expect(main.classes()).toContain('min-h-[calc(100vh-4rem)]')
  })
})

