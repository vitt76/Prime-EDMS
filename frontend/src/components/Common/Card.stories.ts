import type { Meta, StoryObj } from '@storybook/vue3'
import Card from './Card.vue'

const meta: Meta<typeof Card> = {
  title: 'Common/Card',
  component: Card,
  tags: ['autodocs']
}

export default meta
type Story = StoryObj<typeof Card>

export const Default: Story = {
  args: {
    default: 'Card content goes here'
  },
  render: (args) => ({
    components: { Card },
    setup() {
      return { args }
    },
    template: '<Card>Card content</Card>'
  })
}

export const WithHeader: Story = {
  render: () => ({
    components: { Card },
    template: `
      <Card>
        <template #header>
          <h3>Card Header</h3>
        </template>
        Card body content
      </Card>
    `
  })
}

export const WithFooter: Story = {
  render: () => ({
    components: { Card },
    template: `
      <Card>
        Card body content
        <template #footer>
          <button>Action</button>
        </template>
      </Card>
    `
  })
}
