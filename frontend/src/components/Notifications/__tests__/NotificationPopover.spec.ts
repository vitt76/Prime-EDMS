import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

import NotificationPopover from '../NotificationPopover.vue'
import { useNotificationStore } from '@/stores/notificationStore'

describe('NotificationPopover', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders empty state when no notifications', () => {
    const store = useNotificationStore()
    store.centerNotifications = []
    store.centerUnreadCount = 0
    store.setCenterFilter('all')
    store.markAllCenterAsRead = vi.fn()

    const router = createRouter({ history: createWebHistory(), routes: [] })

    const wrapper = mount(NotificationPopover, {
      global: {
        plugins: [router],
        stubs: {
          NotificationCard: true
        }
      }
    })

    expect(wrapper.text()).toContain('Нет уведомлений')
  })
})


