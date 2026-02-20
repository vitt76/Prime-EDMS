import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import AdminPage from '@/pages/AdminPage.vue'

// Hoist so vi.mock can reference them
const { mockRouter, defaultRoute, mockUseRoute } = vi.hoisted(() => {
  const def = { path: '/admin/users', params: {} as Record<string, string>, query: {} as Record<string, string> }
  return {
    mockRouter: { push: vi.fn(), go: vi.fn() },
    defaultRoute: def,
    mockUseRoute: vi.fn(() => def)
  }
})

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: mockUseRoute
  }
})

// AdminPage.vue calls authStore.hasPermission.value('admin.access') — store must expose hasPermission as { value: fn }
const mockHasPermissionValue = vi.fn(() => true)
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(() => ({
    isAuthenticated: true,
    permissions: ['admin.access'],
    hasPermission: { value: mockHasPermissionValue },
    user: { id: '1', email: 'admin@test.com' }
  }))
}))

describe('AdminPage', () => {
  let pinia: ReturnType<typeof createPinia>
  let router: ReturnType<typeof createRouter>
  let wrapper: ReturnType<typeof mount>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/admin/:tab?',
          component: AdminPage
        }
      ]
    })
    mockHasPermissionValue.mockReturnValue(true)
  })

  afterEach(() => {
    vi.clearAllMocks()
    mockUseRoute.mockImplementation(() => defaultRoute)
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    wrapper = mount(AdminPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterView: true,
          Breadcrumbs: true,
          AdminNavigationTabs: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('redirects to forbidden if user lacks admin.access permission', async () => {
    mockHasPermissionValue.mockReturnValue(false)

    wrapper = mount(AdminPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterView: true,
          Breadcrumbs: true,
          AdminNavigationTabs: true
        }
      }
    })

    await wrapper.vm.$nextTick()

    expect(mockRouter.push).toHaveBeenCalledWith({ name: 'forbidden' })
  })

  it('syncs current tab from route', async () => {
    mockUseRoute.mockReturnValue({
      path: '/admin/schemas',
      params: {},
      query: {}
    })

    wrapper = mount(AdminPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterView: true,
          Breadcrumbs: true,
          AdminNavigationTabs: true
        }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.currentTab).toBe('schemas')
  })

  it('handles tab change and navigates', async () => {
    wrapper = mount(AdminPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterView: true,
          Breadcrumbs: true,
          AdminNavigationTabs: {
            name: 'AdminNavigationTabs',
            template: '<div data-tabs>AdminNavigationTabs</div>',
            emits: ['tab-change']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()

    const tabsComponent = wrapper.findComponent({ name: 'AdminNavigationTabs' })
    if (tabsComponent.exists()) {
      await tabsComponent.vm.$emit('tab-change', 'workflows')
    } else {
      await wrapper.find('[data-tabs]').vm.$emit('tab-change', 'workflows')
    }

    expect(mockRouter.push).toHaveBeenCalledWith('/admin/workflows')
  })

  it('generates correct breadcrumbs', () => {
    wrapper = mount(AdminPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterView: true,
          Breadcrumbs: true,
          AdminNavigationTabs: true
        }
      }
    })

    wrapper.vm.currentTab = 'users'
    const breadcrumbs = wrapper.vm.breadcrumbs

    expect(breadcrumbs).toHaveLength(3)
    expect(breadcrumbs[0].label).toBe('Home')
    expect(breadcrumbs[1].label).toBe('Administration')
    expect(breadcrumbs[2].label).toBe('User Management')
  })

  it('formats tab names correctly', () => {
    wrapper = mount(AdminPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterView: true,
          Breadcrumbs: true,
          AdminNavigationTabs: true
        }
      }
    })

    expect(wrapper.vm.formatTabName('users')).toBe('User Management')
    expect(wrapper.vm.formatTabName('schemas')).toBe('Metadata Schemas')
    expect(wrapper.vm.formatTabName('workflows')).toBe('Workflow Designer')
    expect(wrapper.vm.formatTabName('unknown')).toBe('unknown')
  })
})



