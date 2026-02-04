/**
 * FormInput Component Tests
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FormInput from '../../components/Forms/FormInput.vue'

describe('FormInput', () => {
  it('renders label correctly', () => {
    const wrapper = mount(FormInput, {
      props: {
        label: 'Email',
        name: 'email'
      }
    })

    expect(wrapper.find('label').text()).toContain('Email')
  })

  it('shows required indicator when required', () => {
    const wrapper = mount(FormInput, {
      props: {
        label: 'Email',
        name: 'email',
        required: true
      }
    })

    expect(wrapper.text()).toContain('*')
  })

  it('displays error message', () => {
    const wrapper = mount(FormInput, {
      props: {
        label: 'Email',
        name: 'email',
        error: 'Invalid email'
      }
    })

    expect(wrapper.text()).toContain('Invalid email')
  })

  it('displays hint text when no error', () => {
    const wrapper = mount(FormInput, {
      props: {
        label: 'Password',
        name: 'password',
        hint: 'At least 8 characters'
      }
    })

    expect(wrapper.text()).toContain('At least 8 characters')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(FormInput, {
      props: {
        label: 'Email',
        name: 'email',
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    await input.setValue('test@example.com')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['test@example.com'])
  })

  it('sets aria-invalid when error is present', () => {
    const wrapper = mount(FormInput, {
      props: {
        label: 'Email',
        name: 'email',
        error: 'Invalid'
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('aria-invalid')).toBe('true')
  })

  it('applies disabled state', () => {
    const wrapper = mount(FormInput, {
      props: {
        label: 'Email',
        name: 'email',
        disabled: true
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('disabled')).toBeDefined()
  })

  it('renders placeholder', () => {
    const wrapper = mount(FormInput, {
      props: {
        label: 'Email',
        name: 'email',
        placeholder: 'Enter your email'
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('placeholder')).toBe('Enter your email')
  })
})
