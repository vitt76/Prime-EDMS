import type { Meta, StoryObj } from '@storybook/vue3'
import Input from './Input.vue'

const meta: Meta<typeof Input> = {
  title: 'Common/Input',
  component: Input,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['text', 'email', 'password', 'number', 'tel', 'url']
    }
  }
}

export default meta
type Story = StoryObj<typeof Input>

export const Default: Story = {
  args: {
    modelValue: '',
    placeholder: 'Enter text...'
  }
}

export const WithLabel: Story = {
  args: {
    modelValue: '',
    label: 'Email Address',
    placeholder: 'you@example.com',
    type: 'email'
  }
}

export const WithError: Story = {
  args: {
    modelValue: '',
    label: 'Email Address',
    error: 'Please enter a valid email address',
    type: 'email'
  }
}

export const WithHint: Story = {
  args: {
    modelValue: '',
    label: 'Password',
    hint: 'Must be at least 8 characters',
    type: 'password'
  }
}

export const Required: Story = {
  args: {
    modelValue: '',
    label: 'Username',
    required: true
  }
}

export const Disabled: Story = {
  args: {
    modelValue: 'Disabled input',
    label: 'Disabled Field',
    disabled: true
  }
}


