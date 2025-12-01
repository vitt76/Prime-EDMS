import type { Meta, StoryObj } from '@storybook/vue3'
import Sidebar from './Sidebar.vue'

const meta: Meta<typeof Sidebar> = {
  title: 'Layout/Sidebar',
  component: Sidebar,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
}

export default meta
type Story = StoryObj<typeof Sidebar>

export const Expanded: Story = {
  args: {}
}

export const Collapsed: Story = {
  args: {},
  setup() {
    // Mock collapsed state
    return {}
  }
}

