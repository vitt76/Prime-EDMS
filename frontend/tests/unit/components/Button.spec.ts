import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/Common/Button.vue'

describe('Button', () => {
  it('renders correctly', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Click me'
      }
    })
    expect(wrapper.text()).toBe('Click me')
  })

  it('applies primary variant', () => {
    const wrapper = mount(Button, {
      props: {
        variant: 'primary'
      }
    })
    expect(wrapper.classes()).toContain('bg-primary-500')
  })

  it('applies disabled state', () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true
      }
    })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('shows loading spinner when loading', () => {
    const wrapper = mount(Button, {
      props: {
        loading: true
      }
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('emits click event', async () => {
    const wrapper = mount(Button)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})


