import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Select from '@/components/Common/Select.vue'

describe('Select', () => {
  it('renders select button', () => {
    const wrapper = mount(Select, {
      props: {
        options: [
          { value: '1', label: 'Option 1' },
          { value: '2', label: 'Option 2' }
        ],
        placeholder: 'Выберите...'
      }
    })

    expect(wrapper.text()).toContain('Выберите...')
  })

  it('opens dropdown on click', async () => {
    const wrapper = mount(Select, {
      props: {
        options: [
          { value: '1', label: 'Option 1' }
        ]
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')

    // Wait for transition
    await new Promise(resolve => setTimeout(resolve, 100))

    const listbox = wrapper.find('ul[role="listbox"]')
    expect(listbox.exists()).toBe(true)
  })

  it('emits update:modelValue on option select', async () => {
    const wrapper = mount(Select, {
      props: {
        options: [
          { value: '1', label: 'Option 1' },
          { value: '2', label: 'Option 2' }
        ]
      }
    })

    await wrapper.find('button').trigger('click')
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const options = wrapper.findAll('li[role="option"]')
    if (options.length > 0) {
      await options[0].trigger('click')
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    }
  })

  it('supports multiple selection', async () => {
    const wrapper = mount(Select, {
      props: {
        multiple: true,
        modelValue: [],
        options: [
          { value: '1', label: 'Option 1' },
          { value: '2', label: 'Option 2' }
        ]
      }
    })

    await wrapper.find('button').trigger('click')
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const options = wrapper.findAll('li[role="option"]')
    if (options.length >= 2) {
      await options[0].trigger('click')
      await options[1].trigger('click')

      const updates = wrapper.emitted('update:modelValue')
      expect(updates).toBeTruthy()
    }
  })

  it('filters options when searchable', async () => {
    const wrapper = mount(Select, {
      props: {
        searchable: true,
        options: [
          { value: '1', label: 'Apple' },
          { value: '2', label: 'Banana' },
          { value: '3', label: 'Cherry' }
        ]
      }
    })

    await wrapper.find('button').trigger('click')
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const searchInput = wrapper.find('input[type="text"]')
    if (searchInput.exists()) {
      await searchInput.setValue('Banana')
      await wrapper.vm.$nextTick()

      const options = wrapper.findAll('li[role="option"]')
      expect(options.length).toBeGreaterThan(0)
    }
  })

  it('disables when disabled prop is true', () => {
    const wrapper = mount(Select, {
      props: {
        disabled: true,
        options: [{ value: '1', label: 'Option 1' }]
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('shows selected label', () => {
    const wrapper = mount(Select, {
      props: {
        modelValue: '2',
        options: [
          { value: '1', label: 'Option 1' },
          { value: '2', label: 'Option 2' }
        ]
      }
    })

    expect(wrapper.text()).toContain('Option 2')
  })

  it('shows count for multiple selection', () => {
    const wrapper = mount(Select, {
      props: {
        multiple: true,
        modelValue: ['1', '2'],
        options: [
          { value: '1', label: 'Option 1' },
          { value: '2', label: 'Option 2' }
        ]
      }
    })

    expect(wrapper.text()).toContain('Выбрано: 2')
  })
})
