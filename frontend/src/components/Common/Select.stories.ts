import type { Meta, StoryObj } from '@storybook/vue3'
import Select from './Select.vue'

const meta: Meta<typeof Select> = {
  title: 'Common/Select',
  component: Select,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { control: 'text' },
    options: { control: 'object' },
    placeholder: { control: 'text' },
    disabled: { control: 'boolean' },
    multiple: { control: 'boolean' },
    searchable: { control: 'boolean' }
  }
}

export default meta
type Story = StoryObj<typeof Select>

export const Default: Story = {
  args: {
    options: [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' }
    ],
    placeholder: 'Выберите опцию...'
  }
}

export const WithValue: Story = {
  args: {
    modelValue: 'option2',
    options: [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' }
    ],
    placeholder: 'Выберите опцию...'
  }
}

export const Multiple: Story = {
  args: {
    multiple: true,
    modelValue: ['option1', 'option2'],
    options: [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' }
    ],
    placeholder: 'Выберите опции...'
  }
}

export const Searchable: Story = {
  args: {
    searchable: true,
    options: [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' }
    ],
    placeholder: 'Поиск...'
  }
}

export const Disabled: Story = {
  args: {
    disabled: true,
    options: [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' }
    ],
    placeholder: 'Недоступно'
  }
}

