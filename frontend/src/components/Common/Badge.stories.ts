import type { Meta, StoryObj } from '@storybook/vue3'
import Badge from './Badge.vue'

const meta: Meta<typeof Badge> = {
  title: 'Common/Badge',
  component: Badge,
  tags: ['autodocs']
}

export default meta
type Story = StoryObj<typeof Badge>

export const Success: Story = {
  args: {
    variant: 'success',
    default: 'Success'
  }
}

export const Warning: Story = {
  args: {
    variant: 'warning',
    default: 'Warning'
  }
}

export const Error: Story = {
  args: {
    variant: 'error',
    default: 'Error'
  }
}

export const Info: Story = {
  args: {
    variant: 'info',
    default: 'Info'
  }
}

export const Neutral: Story = {
  args: {
    variant: 'neutral',
    default: 'Neutral'
  }
}
