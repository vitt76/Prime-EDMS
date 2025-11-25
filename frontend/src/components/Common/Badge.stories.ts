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
    children: 'Success'
  },
  render: (args) => ({
    components: { Badge },
    setup() {
      return { args }
    },
    template: '<Badge v-bind="args">Success</Badge>'
  })
}

export const Warning: Story = {
  args: {
    variant: 'warning',
    children: 'Warning'
  },
  render: (args) => ({
    components: { Badge },
    setup() {
      return { args }
    },
    template: '<Badge v-bind="args">Warning</Badge>'
  })
}

export const Error: Story = {
  args: {
    variant: 'error',
    children: 'Error'
  },
  render: (args) => ({
    components: { Badge },
    setup() {
      return { args }
    },
    template: '<Badge v-bind="args">Error</Badge>'
  })
}

export const Info: Story = {
  args: {
    variant: 'info',
    children: 'Info'
  },
  render: (args) => ({
    components: { Badge },
    setup() {
      return { args }
    },
    template: '<Badge v-bind="args">Info</Badge>'
  })
}

export const Neutral: Story = {
  args: {
    variant: 'neutral',
    children: 'Neutral'
  },
  render: (args) => ({
    components: { Badge },
    setup() {
      return { args }
    },
    template: '<Badge v-bind="args">Neutral</Badge>'
  })
}


