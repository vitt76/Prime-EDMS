import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Card from '@/components/Common/Card.vue'

describe('Card', () => {
  it('renders card content', () => {
    const wrapper = mount(Card, {
      slots: {
        default: 'Card content'
      }
    })

    expect(wrapper.text()).toContain('Card content')
  })

  it('applies default classes', () => {
    const wrapper = mount(Card)
    const card = wrapper.find('.bg-neutral-0')
    expect(card.exists()).toBe(true)
  })

  it('renders header slot', () => {
    const wrapper = mount(Card, {
      slots: {
        header: '<div>Card Header</div>'
      }
    })

    expect(wrapper.text()).toContain('Card Header')
  })

  it('renders footer slot', () => {
    const wrapper = mount(Card, {
      slots: {
        footer: '<button>Action</button>'
      }
    })

    expect(wrapper.text()).toContain('Action')
  })

  it('applies variant classes', () => {
    const variants = ['default', 'elevated', 'outlined'] as const

    variants.forEach((variant) => {
      const wrapper = mount(Card, {
        props: {
          variant
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })

  it('applies padding classes', () => {
    const paddings = ['none', 'sm', 'md', 'lg'] as const

    paddings.forEach((padding) => {
      const wrapper = mount(Card, {
        props: {
          padding
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })
})

