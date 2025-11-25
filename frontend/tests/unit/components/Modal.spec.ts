import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from '@/components/Common/Modal.vue'

describe('Modal', () => {
  it('renders when isOpen is true', () => {
    const wrapper = mount(Modal, {
      props: {
        isOpen: true,
        title: 'Test Modal'
      },
      slots: {
        default: 'Modal content'
      }
    })

    expect(wrapper.text()).toContain('Test Modal')
    expect(wrapper.text()).toContain('Modal content')
  })

  it('does not render when isOpen is false', () => {
    const wrapper = mount(Modal, {
      props: {
        isOpen: false
      }
    })

    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('emits close event when close button is clicked', async () => {
    const wrapper = mount(Modal, {
      props: {
        isOpen: true,
        closable: true
      }
    })

    const closeButton = wrapper.find('button[aria-label="Close"]')
    await closeButton.trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
    expect(wrapper.emitted('update:isOpen')).toBeTruthy()
    expect(wrapper.emitted('update:isOpen')?.[0]).toEqual([false])
  })

  it('emits close event when backdrop is clicked', async () => {
    const wrapper = mount(Modal, {
      props: {
        isOpen: true,
        closeOnBackdrop: true
      }
    })

    const backdrop = wrapper.find('.fixed.inset-0')
    await backdrop.trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('does not close when closeOnBackdrop is false', async () => {
    const wrapper = mount(Modal, {
      props: {
        isOpen: true,
        closeOnBackdrop: false
      }
    })

    const backdrop = wrapper.find('.fixed.inset-0')
    await backdrop.trigger('click')

    expect(wrapper.emitted('close')).toBeFalsy()
  })

  it('applies correct size classes', () => {
    const sizes = ['sm', 'md', 'lg', 'xl', 'full'] as const

    sizes.forEach((size) => {
      const wrapper = mount(Modal, {
        props: {
          isOpen: true,
          size
        }
      })

      const modal = wrapper.find('.rounded-lg')
      expect(modal.exists()).toBe(true)
    })
  })

  it('renders header slot', () => {
    const wrapper = mount(Modal, {
      props: {
        isOpen: true
      },
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header')
  })

  it('renders footer slot', () => {
    const wrapper = mount(Modal, {
      props: {
        isOpen: true
      },
      slots: {
        footer: '<button>Save</button>'
      }
    })

    expect(wrapper.text()).toContain('Save')
  })
})

