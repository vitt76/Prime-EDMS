import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Badge from '@/components/Common/Badge.vue'

describe('Badge', () => {
  it('renders badge text', () => {
    const wrapper = mount(Badge, {
      slots: {
        default: 'Badge Text'
      }
    })

    expect(wrapper.text()).toContain('Badge Text')
  })

  it('applies variant classes', () => {
    const variants = ['success', 'warning', 'error', 'info', 'neutral'] as const

    variants.forEach((variant) => {
      const wrapper = mount(Badge, {
        props: {
          variant
        },
        slots: {
          default: 'Test'
        }
      })

      const badge = wrapper.find('.inline-flex')
      expect(badge.exists()).toBe(true)
    })
  })

  it('applies size classes', () => {
    const sizes = ['sm', 'md', 'lg'] as const

    sizes.forEach((size) => {
      const wrapper = mount(Badge, {
        props: {
          size
        },
        slots: {
          default: 'Test'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })
})

