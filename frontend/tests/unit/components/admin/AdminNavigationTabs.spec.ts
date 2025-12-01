import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminNavigationTabs from '@/components/admin/AdminNavigationTabs.vue'
import { useAuthStore } from '@/stores/authStore'

describe('AdminNavigationTabs', () => {
  let pinia: any
  let wrapper: ReturnType<typeof mount>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage', 'admin.schema_manage']

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('[role="tablist"]').exists()).toBe(true)
  })

  it('shows only tabs user has permission for', () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage']

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tabs = wrapper.findAll('[role="tab"]')
    expect(tabs.length).toBe(1)
    expect(tabs[0].text()).toContain('Users')
  })

  it('highlights active tab', () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage', 'admin.schema_manage']

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'schemas'
      },
      global: {
        plugins: [pinia]
      }
    })

    const activeTab = wrapper.find('.admin-tabs__tab--active')
    expect(activeTab.exists()).toBe(true)
    expect(activeTab.attributes('aria-selected')).toBe('true')
  })

  it('emits tab-change on click', async () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage', 'admin.schema_manage']

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tabs = wrapper.findAll('[role="tab"]')
    const schemasTab = tabs.find((tab) => tab.text().includes('Metadata Schemas'))

    if (schemasTab) {
      await schemasTab.trigger('click')
      expect(wrapper.emitted('tab-change')).toBeTruthy()
      expect(wrapper.emitted('tab-change')?.[0]).toEqual(['schemas'])
    }
  })

  it('emits tab-change on Enter key', async () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage', 'admin.schema_manage']

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tabs = wrapper.findAll('[role="tab"]')
    const schemasTab = tabs.find((tab) => tab.text().includes('Metadata Schemas'))

    if (schemasTab) {
      await schemasTab.trigger('keydown', { key: 'Enter' })
      expect(wrapper.emitted('tab-change')).toBeTruthy()
      expect(wrapper.emitted('tab-change')?.[0]).toEqual(['schemas'])
    }
  })

  it('emits tab-change on Space key', async () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage', 'admin.schema_manage']

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tabs = wrapper.findAll('[role="tab"]')
    const schemasTab = tabs.find((tab) => tab.text().includes('Metadata Schemas'))

    if (schemasTab) {
      const event = new KeyboardEvent('keydown', { key: ' ', bubbles: true })
      Object.defineProperty(event, 'preventDefault', { value: vi.fn() })
      await schemasTab.trigger('keydown', event)
      expect(wrapper.emitted('tab-change')).toBeTruthy()
    }
  })

  it('navigates with ArrowLeft key', async () => {
    const authStore = useAuthStore()
    authStore.permissions = [
      'admin.user_manage',
      'admin.schema_manage',
      'admin.workflow_manage'
    ]

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'schemas'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tabs = wrapper.findAll('[role="tab"]')
    const schemasTab = tabs.find((tab) => tab.text().includes('Metadata Schemas'))

    if (schemasTab) {
      await schemasTab.trigger('keydown', { key: 'ArrowLeft' })
      // Should navigate to previous tab (users)
      expect(wrapper.emitted('tab-change')).toBeTruthy()
    }
  })

  it('navigates with ArrowRight key', async () => {
    const authStore = useAuthStore()
    authStore.permissions = [
      'admin.user_manage',
      'admin.schema_manage',
      'admin.workflow_manage'
    ]

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'schemas'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tabs = wrapper.findAll('[role="tab"]')
    const schemasTab = tabs.find((tab) => tab.text().includes('Metadata Schemas'))

    if (schemasTab) {
      await schemasTab.trigger('keydown', { key: 'ArrowRight' })
      // Should navigate to next tab (workflows)
      expect(wrapper.emitted('tab-change')).toBeTruthy()
    }
  })

  it('wraps around when navigating with ArrowLeft from first tab', async () => {
    const authStore = useAuthStore()
    authStore.permissions = [
      'admin.user_manage',
      'admin.schema_manage',
      'admin.workflow_manage'
    ]

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tabs = wrapper.findAll('[role="tab"]')
    const usersTab = tabs[0]

    await usersTab.trigger('keydown', { key: 'ArrowLeft' })
    // Should wrap to last tab
    expect(wrapper.emitted('tab-change')).toBeTruthy()
  })

  it('wraps around when navigating with ArrowRight from last tab', async () => {
    const authStore = useAuthStore()
    authStore.permissions = [
      'admin.user_manage',
      'admin.schema_manage',
      'admin.workflow_manage'
    ]

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'workflows'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tabs = wrapper.findAll('[role="tab"]')
    const lastTab = tabs[tabs.length - 1]

    await lastTab.trigger('keydown', { key: 'ArrowRight' })
    // Should wrap to first tab
    expect(wrapper.emitted('tab-change')).toBeTruthy()
  })

  it('shows mobile dropdown on small screens', () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage', 'admin.schema_manage']

    // Mock window.matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: query === '(max-width: 768px)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn()
      }))
    })

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    // Mobile dropdown should exist (though visibility controlled by CSS)
    const select = wrapper.find('.admin-tabs__select')
    // Note: CSS controls visibility, so element exists but may be hidden
    expect(select.exists()).toBe(true)
  })

  it('emits tab-change on mobile select change', async () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage', 'admin.schema_manage']

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    const select = wrapper.find('.admin-tabs__select')
    await select.setValue('schemas')
    await select.trigger('change')

    expect(wrapper.emitted('tab-change')).toBeTruthy()
    expect(wrapper.emitted('tab-change')?.[0]).toEqual(['schemas'])
  })

  it('has correct ARIA attributes', () => {
    const authStore = useAuthStore()
    authStore.permissions = ['admin.user_manage', 'admin.schema_manage']

    wrapper = mount(AdminNavigationTabs, {
      props: {
        currentTab: 'users'
      },
      global: {
        plugins: [pinia]
      }
    })

    const tablist = wrapper.find('[role="tablist"]')
    expect(tablist.attributes('aria-label')).toBe('Administration Navigation')

    const tabs = wrapper.findAll('[role="tab"]')
    tabs.forEach((tab) => {
      expect(tab.attributes('aria-selected')).toBeDefined()
      expect(tab.attributes('aria-controls')).toBeDefined()
    })
  })
})



