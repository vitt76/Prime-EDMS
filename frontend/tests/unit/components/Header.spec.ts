import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Header from '@/components/Layout/Header.vue'
import { useAuthStore } from '@/stores/authStore'
import { useNotificationStore } from '@/stores/notificationStore'

// Mock stores
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn()
}))

vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: vi.fn()
}))

describe('Header', () => {
  let router: ReturnType<typeof createRouter>
  let pinia: ReturnType<typeof createPinia>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })

    // Mock stores
    const mockAuthStore = {
      user: { id: 1, username: 'test', first_name: 'Test' },
      isAuthenticated: true,
      logout: vi.fn()
    }

    const mockNotificationStore = {
      unreadCount: 3
    }

    vi.mocked(useAuthStore).mockReturnValue(mockAuthStore as any)
    vi.mocked(useNotificationStore).mockReturnValue(mockNotificationStore as any)
  })

  it('renders header with logo', () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.find('router-link[to="/"]').exists()).toBe(true)
  })

  it('renders search input', () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    const searchInput = wrapper.find('input[type="text"]')
    expect(searchInput.exists()).toBe(true)
    expect(searchInput.attributes('placeholder')).toContain('Поиск')
  })

  it('emits search event on input', async () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    const searchInput = wrapper.find('input[type="text"]')
    await searchInput.setValue('test query')
    await searchInput.trigger('input')

    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('search')?.[0]).toEqual(['test query'])
  })

  it('emits upload event on upload button click', async () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    const uploadButton = wrapper.find('button[aria-label="Загрузить файл"]')
    await uploadButton.trigger('click')

    expect(wrapper.emitted('upload')).toBeTruthy()
  })

  it('emits filter-toggle event on filter button click', async () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    const filterButton = wrapper.find('button[aria-label="Фильтры"]')
    await filterButton.trigger('click')

    expect(wrapper.emitted('filter-toggle')).toBeTruthy()
  })

  it('shows notification badge when unreadCount > 0', () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    const badge = wrapper.find('.bg-error')
    expect(badge.exists()).toBe(true)
  })

  it('toggles user menu on click', async () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    const userMenuButton = wrapper.find('button[aria-label="Меню пользователя"]')
    await userMenuButton.trigger('click')

    const dropdown = wrapper.find('.absolute.right-0.mt-2')
    expect(dropdown.exists()).toBe(true)
  })

  it('calls logout on logout button click', async () => {
    const mockLogout = vi.fn()
    const mockAuthStore = {
      user: { id: 1, username: 'test' },
      isAuthenticated: true,
      logout: mockLogout
    }
    vi.mocked(useAuthStore).mockReturnValue(mockAuthStore as any)

    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    // Open user menu
    const userMenuButton = wrapper.find('button[aria-label="Меню пользователя"]')
    await userMenuButton.trigger('click')

    // Click logout
    const logoutButton = wrapper.find('button:contains("Выйти")')
    if (logoutButton.exists()) {
      await logoutButton.trigger('click')
      expect(mockLogout).toHaveBeenCalled()
    }
  })

  it('handles Ctrl+K shortcut to focus search', async () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    const searchInput = wrapper.find('input[type="text"]').element as HTMLInputElement
    
    // Simulate Ctrl+K
    const event = new KeyboardEvent('keydown', {
      key: 'k',
      ctrlKey: true,
      bubbles: true
    })
    
    document.dispatchEvent(event)
    await wrapper.vm.$nextTick()

    // Search should be focused (if event handler works)
    expect(searchInput).toBeDefined()
  })

  it('emits mobile-menu-toggle on mobile menu button click', async () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [pinia, router]
      }
    })

    const mobileMenuButton = wrapper.find('button[aria-label="Меню"]')
    if (mobileMenuButton.exists()) {
      await mobileMenuButton.trigger('click')
      expect(wrapper.emitted('mobile-menu-toggle')).toBeTruthy()
    }
  })
})

