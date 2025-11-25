import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Input from '@/components/Common/Input.vue'

describe('Input', () => {
  it('renders correctly', () => {
    const wrapper = mount(Input, {
      props: {
        modelValue: ''
      }
    })
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('displays label', () => {
    const wrapper = mount(Input, {
      props: {
        modelValue: '',
        label: 'Email'
      }
    })
    expect(wrapper.text()).toContain('Email')
  })

  it('displays error message', () => {
    const wrapper = mount(Input, {
      props: {
        modelValue: '',
        error: 'This field is required'
      }
    })
    expect(wrapper.text()).toContain('This field is required')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(Input, {
      props: {
        modelValue: ''
      }
    })
    const input = wrapper.find('input')
    await input.setValue('test@example.com')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['test@example.com'])
  })
})


