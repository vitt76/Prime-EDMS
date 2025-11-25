import type { Meta, StoryObj } from '@storybook/vue3'
import Header from './Header.vue'

const meta: Meta<typeof Header> = {
  title: 'Layout/Header',
  component: Header,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
}

export default meta
type Story = StoryObj<typeof Header>

export const Default: Story = {
  args: {}
}

