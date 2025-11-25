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
  render: () => ({
    components: { Card },
    template: `
      <Card>
        <p>This is a default card with some content.</p>
      </Card>
    `
  })
}

export const WithHeader: Story = {
  render: () => ({
    components: { Card },
    template: `
      <Card>
        <template #header>
          <h3 class="font-semibold">Card Header</h3>
        </template>
        <p>Card content goes here.</p>
        <template #footer>
          <button class="text-primary-500">Action</button>
        </template>
      </Card>
    `
  })
}

export const Elevated: Story = {
  render: () => ({
    components: { Card },
    template: `
      <Card variant="elevated">
        <p>This card has elevated shadow.</p>
      </Card>
    `
  })
}


