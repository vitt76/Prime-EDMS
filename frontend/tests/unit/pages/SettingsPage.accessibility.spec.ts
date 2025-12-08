import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { render } from '@testing-library/vue'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import SettingsPage from '@/pages/SettingsPage.vue'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import { axe, toHaveNoViolations } from 'vitest-axe'

expect.extend(toHaveNoViolations)

describe('SettingsPage Accessibility', () => {
  let pinia: any
  let router: any
  let container: HTMLElement

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

    localStorage.clear()
  })

  afterEach(() => {
    if (container) {
      container.remove()
    }
    localStorage.clear()
  })

  it('should have no accessibility violations', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have proper form labels', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    // Check that all inputs have associated labels
    const inputs = container.querySelectorAll('input, select')
    inputs.forEach(input => {
      const id = input.getAttribute('id')
      if (id) {
        const label = container.querySelector(`label[for="${id}"]`)
        expect(label).toBeTruthy()
      }
    })
  })

  it('should have proper ARIA labels for buttons', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    const saveButton = container.querySelector('button[aria-label="Сохранить изменения профиля"]')
    expect(saveButton).toBeTruthy()

    const changePasswordButton = container.querySelector('button[aria-label="Изменить пароль"]')
    expect(changePasswordButton).toBeTruthy()

    const apiKeysButton = container.querySelector('button[aria-label="Управление API ключами"]')
    expect(apiKeysButton).toBeTruthy()
  })

  it('should have proper ARIA labels for checkboxes', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    const emailCheckbox = container.querySelector('#email-notifications')
    expect(emailCheckbox).toBeTruthy()
    expect(emailCheckbox?.getAttribute('aria-label')).toBe('Включить email уведомления')

    const pushCheckbox = container.querySelector('#push-notifications')
    expect(pushCheckbox).toBeTruthy()
    expect(pushCheckbox?.getAttribute('aria-label')).toBe('Включить push уведомления')

    const inAppCheckbox = container.querySelector('#in-app-notifications')
    expect(inAppCheckbox).toBeTruthy()
    expect(inAppCheckbox?.getAttribute('aria-label')).toBe('Включить внутренние уведомления')
  })

  it('should have proper semantic HTML structure', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    // Check for heading hierarchy
    const h1 = container.querySelector('h1')
    expect(h1).toBeTruthy()
    expect(h1?.textContent).toContain('Настройки')

    const h2s = container.querySelectorAll('h2')
    expect(h2s.length).toBeGreaterThan(0)
  })

  it('should have proper color contrast (WCAG AA)', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    const results = await axe(container, {
      rules: {
        'color-contrast': { enabled: true }
      }
    })

    const contrastViolations = results.violations.filter(
      v => v.id === 'color-contrast'
    )
    expect(contrastViolations.length).toBe(0)
  })

  it('should have keyboard navigation support', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    const interactiveElements = container.querySelectorAll(
      'button, a, input, select, [role="button"], [tabindex="0"]'
    )
    
    interactiveElements.forEach(element => {
      // All interactive elements should be focusable
      const tabindex = element.getAttribute('tabindex')
      if (tabindex !== null) {
        expect(tabindex).not.toBe('-1')
      }
    })
  })

  it('should have proper focus indicators', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    const results = await axe(container, {
      rules: {
        'focus-order-semantics': { enabled: true },
        'focusable-content': { enabled: true }
      }
    })

    const focusViolations = results.violations.filter(
      v => v.id === 'focus-order-semantics' || v.id === 'focusable-content'
    )
    expect(focusViolations.length).toBe(0)
  })

  it('should have minimum touch target sizes (44px)', async () => {
    const { container: renderedContainer } = render(SettingsPage, {
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

    container = renderedContainer

    const interactiveElements = container.querySelectorAll(
      'button, a, input[type="checkbox"], [role="button"]'
    )

    interactiveElements.forEach(element => {
      const styles = window.getComputedStyle(element as HTMLElement)
      const minHeight = parseInt(styles.minHeight) || parseInt(styles.height) || 0
      const minWidth = parseInt(styles.minWidth) || parseInt(styles.width) || 0

      // Check that touch targets are at least 44px (WCAG 2.1 AA)
      if (minHeight > 0) {
        expect(minHeight).toBeGreaterThanOrEqual(44)
      }
      if (minWidth > 0) {
        expect(minWidth).toBeGreaterThanOrEqual(44)
      }
    })
  })
})















