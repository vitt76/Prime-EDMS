import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

import NotificationBell from '../NotificationBell.vue'
import { useNotificationStore } from '@/stores/notificationStore'

vi.mock('@/hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    connect: vi.fn(),
    disconnect: vi.fn()
  })
}))

describe('NotificationBell', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders badge when unread > 0', async () => {
    const store = useNotificationStore()
    // Avoid real API calls during tests.
    store.getCenterUnreadCount = vi.fn()
    store.fetchCenterNotifications = vi.fn()
    store.centerUnreadCount = 2

    const wrapper = mount(NotificationBell, {
      global: {
        stubs: {
          NotificationPopover: true
        }
      }
    })

    expect(wrapper.find('span.absolute.top-1.right-1').exists()).toBe(true)
  })

  it('toggles popover on click', async () => {
    const store = useNotificationStore()
    store.getCenterUnreadCount = vi.fn()
    store.fetchCenterNotifications = vi.fn()

    const wrapper = mount(NotificationBell, {
      global: {
        stubs: {
          NotificationPopover: { template: '<div data-test=\"popover\" />' }
        }
      }
    })

    expect(wrapper.find('[data-test="popover"]').exists()).toBe(false)
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('[data-test="popover"]').exists()).toBe(true)
  })
})


