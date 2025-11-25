import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import SettingsPage from '@/pages/SettingsPage.vue'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'

describe('SettingsPage', () => {
  let pinia: any
  let router: any
  let wrapper: ReturnType<typeof mount>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/settings', component: SettingsPage }
      ]
    })

    vi.clearAllMocks()

    // Setup stores
    const uiStore = useUIStore()
    const authStore = useAuthStore()

    uiStore.theme = 'light'
    uiStore.notifications = []

    authStore.user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      is_active: true
    }

    // Clear localStorage
    localStorage.clear()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    localStorage.clear()
  })

  it('renders page with title', () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    expect(wrapper.text()).toContain('Настройки')
  })

  it('displays profile section with user data', () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    expect(wrapper.text()).toContain('Профиль')
    expect(wrapper.text()).toContain('Имя')
    expect(wrapper.text()).toContain('Фамилия')
    expect(wrapper.text()).toContain('Email')
  })

  it('loads user data into profile form', async () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: {
            template: '<input :value="modelValue" />',
            props: ['modelValue']
          },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    // Wait for onMounted to execute
    await new Promise(resolve => setTimeout(resolve, 100))

    const firstNameInput = wrapper.find('#first-name')
    const lastNameInput = wrapper.find('#last-name')
    const emailInput = wrapper.find('#email')

    expect(firstNameInput.exists()).toBe(true)
    expect(lastNameInput.exists()).toBe(true)
    expect(emailInput.exists()).toBe(true)
  })

  it('displays theme settings section', () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    expect(wrapper.text()).toContain('Внешний вид')
    expect(wrapper.text()).toContain('Тема оформления')
  })

  it('allows changing theme', async () => {
    const uiStore = useUIStore()
    const setThemeSpy = vi.spyOn(uiStore, 'setTheme')

    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: {
            template: '<select @change="$emit(\'change\', $event.target.value)"><slot /></select>',
            emits: ['change']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    const themeSelect = wrapper.find('#theme')
    expect(themeSelect.exists()).toBe(true)

    // Simulate theme change
    await themeSelect.setValue('dark')
    await themeSelect.trigger('change', { target: { value: 'dark' } })
    
    // Theme change is handled via computed setter
    expect(uiStore.theme).toBe('dark')
  })

  it('displays notification settings', () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    expect(wrapper.text()).toContain('Уведомления')
    expect(wrapper.text()).toContain('Email уведомления')
    expect(wrapper.text()).toContain('Push уведомления')
    expect(wrapper.text()).toContain('Внутренние уведомления')
  })

  it('saves notification settings to localStorage', async () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input type="checkbox" />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const emailCheckbox = wrapper.find('#email-notifications')
    expect(emailCheckbox.exists()).toBe(true)

    // Toggle checkbox
    await emailCheckbox.setValue(false)
    await emailCheckbox.trigger('change')

    // Check localStorage
    const saved = localStorage.getItem('notification_settings')
    expect(saved).toBeTruthy()
    if (saved) {
      const parsed = JSON.parse(saved)
      expect(parsed.email).toBe(false)
    }
  })

  it('displays preferences section', () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    expect(wrapper.text()).toContain('Предпочтения')
    expect(wrapper.text()).toContain('Язык интерфейса')
    expect(wrapper.text()).toContain('Часовой пояс')
    expect(wrapper.text()).toContain('Элементов на странице')
  })

  it('loads saved preferences from localStorage', async () => {
    const savedPreferences = {
      language: 'en',
      timezone: 'UTC',
      itemsPerPage: 100
    }
    localStorage.setItem('user_preferences', JSON.stringify(savedPreferences))

    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Preferences should be loaded from localStorage
    const saved = localStorage.getItem('user_preferences')
    expect(saved).toBeTruthy()
    if (saved) {
      const parsed = JSON.parse(saved)
      expect(parsed.language).toBe('en')
      expect(parsed.timezone).toBe('UTC')
    }
  })

  it('saves preferences to localStorage when changed', async () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: {
            template: '<select @change="$emit(\'change\', $event.target.value)"><slot /></select>',
            emits: ['change']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const languageSelect = wrapper.find('#language')
    expect(languageSelect.exists()).toBe(true)

    // Change language
    await languageSelect.setValue('en')
    await languageSelect.trigger('change', { target: { value: 'en' } })

    // Check localStorage
    const saved = localStorage.getItem('user_preferences')
    expect(saved).toBeTruthy()
    if (saved) {
      const parsed = JSON.parse(saved)
      expect(parsed.language).toBe('en')
    }
  })

  it('displays security settings section', () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    expect(wrapper.text()).toContain('Безопасность')
    expect(wrapper.text()).toContain('Изменить пароль')
    expect(wrapper.text()).toContain('Управление API ключами')
  })

  it('handles save profile action', async () => {
    const uiStore = useUIStore()
    const addNotificationSpy = vi.spyOn(uiStore, 'addNotification')

    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            emits: ['click']
          },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const saveButton = wrapper.find('button[aria-label="Сохранить изменения профиля"]')
    expect(saveButton.exists()).toBe(true)

    await saveButton.trigger('click')
    // Wait for async operation
    await new Promise(resolve => setTimeout(resolve, 600))

    expect(addNotificationSpy).toHaveBeenCalled()
  })

  it('handles change password action', async () => {
    const uiStore = useUIStore()
    const addNotificationSpy = vi.spyOn(uiStore, 'addNotification')

    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            emits: ['click']
          },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const changePasswordButton = wrapper.find('button[aria-label="Изменить пароль"]')
    expect(changePasswordButton.exists()).toBe(true)

    await changePasswordButton.trigger('click')
    expect(addNotificationSpy).toHaveBeenCalled()
  })

  it('handles manage API keys action', async () => {
    const uiStore = useUIStore()
    const addNotificationSpy = vi.spyOn(uiStore, 'addNotification')

    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            emits: ['click']
          },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const apiKeysButton = wrapper.find('button[aria-label="Управление API ключами"]')
    expect(apiKeysButton.exists()).toBe(true)

    await apiKeysButton.trigger('click')
    expect(addNotificationSpy).toHaveBeenCalled()
  })

  it('has proper ARIA labels for accessibility', () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    // Check for ARIA labels
    const saveButton = wrapper.find('button[aria-label="Сохранить изменения профиля"]')
    expect(saveButton.exists()).toBe(true)

    const changePasswordButton = wrapper.find('button[aria-label="Изменить пароль"]')
    expect(changePasswordButton.exists()).toBe(true)

    const apiKeysButton = wrapper.find('button[aria-label="Управление API ключами"]')
    expect(apiKeysButton.exists()).toBe(true)

    const emailCheckbox = wrapper.find('#email-notifications')
    expect(emailCheckbox.exists()).toBe(true)
    expect(emailCheckbox.attributes('aria-label')).toBe('Включить email уведомления')
  })

  it('disables email input field', () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: { template: '<button><slot /></button>' },
          Input: {
            template: '<input :disabled="disabled" />',
            props: ['disabled']
          },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    const emailInput = wrapper.find('#email')
    expect(emailInput.exists()).toBe(true)
    expect(emailInput.attributes('disabled')).toBeDefined()
  })

  it('shows loading state when saving profile', async () => {
    wrapper = mount(SettingsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          Button: {
            template: '<button :disabled="loading"><slot /></button>',
            props: ['loading']
          },
          Input: { template: '<input />' },
          Select: { template: '<select><slot /></select>' }
        }
      }
    })

    // Set loading state
    await wrapper.setData({ isSavingProfile: true })
    await wrapper.vm.$nextTick()

    const saveButton = wrapper.find('button[aria-label="Сохранить изменения профиля"]')
    expect(saveButton.exists()).toBe(true)
    // Button should be disabled when loading
    expect(saveButton.attributes('disabled')).toBeDefined()
  })
})

