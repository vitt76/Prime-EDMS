import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import AdminPage from '@/pages/AdminPage.vue'
import { useAuthStore } from '@/stores/authStore'

// Mock router
const mockRouter = {
  push: vi.fn(),
  go: vi.fn()
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => ({
      path: '/admin/users',
      params: {},
      query: {}
    })
  }
})

describe('AdminPage', () => {
  let pinia: any
  let router: any
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
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    const authStore = useAuthStore()
    authStore.isAuthenticated = true
    authStore.permissions = ['admin.access']

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
    const authStore = useAuthStore()
    authStore.isAuthenticated = true
    authStore.permissions = []

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
    const authStore = useAuthStore()
    authStore.isAuthenticated = true
    authStore.permissions = ['admin.access']

    const route = {
      path: '/admin/schemas',
      params: {},
      query: {}
    }

    vi.mocked(require('vue-router').useRoute).mockReturnValue(route as any)

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
    const authStore = useAuthStore()
    authStore.isAuthenticated = true
    authStore.permissions = ['admin.access']

    wrapper = mount(AdminPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterView: true,
          Breadcrumbs: true,
          AdminNavigationTabs: {
            template: '<div>AdminNavigationTabs</div>',
            emits: ['tab-change']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()

    const tabsComponent = wrapper.findComponent({ name: 'AdminNavigationTabs' })
    await tabsComponent.vm.$emit('tab-change', 'workflows')

    expect(mockRouter.push).toHaveBeenCalledWith('/admin/workflows')
  })

  it('generates correct breadcrumbs', () => {
    const authStore = useAuthStore()
    authStore.isAuthenticated = true
    authStore.permissions = ['admin.access']

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
    const authStore = useAuthStore()
    authStore.isAuthenticated = true
    authStore.permissions = ['admin.access']

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



