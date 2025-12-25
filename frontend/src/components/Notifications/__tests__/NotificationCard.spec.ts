import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import NotificationCard from '../NotificationCard.vue'

describe('NotificationCard', () => {
  it('renders title and message', () => {
    const wrapper = mount(NotificationCard, {
      props: {
        notification: {
          id: 1,
          uuid: 'u',
          title: 'Title',
          message: 'Message',
          event_type: 'evt',
          priority: 'NORMAL',
          state: 'SENT',
          icon_type: 'info',
          created_at: '2025-12-25T00:00:00Z'
        }
      }
    })

    expect(wrapper.text()).toContain('Title')
    expect(wrapper.text()).toContain('Message')
  })
})


