import type { Meta, StoryObj } from '@storybook/vue3'
import Modal from './Modal.vue'

const meta: Meta<typeof Modal> = {
  title: 'Common/Modal',
  component: Modal,
  tags: ['autodocs'],
  argTypes: {
    isOpen: { control: 'boolean' },
    title: { control: 'text' },
    size: { control: 'select', options: ['sm', 'md', 'lg', 'xl', 'full'] },
    closable: { control: 'boolean' },
    closeOnBackdrop: { control: 'boolean' }
  }
}

export default meta
type Story = StoryObj<typeof Modal>

export const Default: Story = {
  args: {
    isOpen: true,
    title: 'Modal Title',
    size: 'md',
    closable: true,
    closeOnBackdrop: true
  },
  render: (args) => ({
    components: { Modal },
    setup() {
      return { args }
    },
    template: `
      <Modal v-bind="args">
        <p>This is the modal content. You can add any content here.</p>
      </Modal>
    `
  })
}

export const Large: Story = {
  args: {
    isOpen: true,
    title: 'Large Modal',
    size: 'lg'
  },
  render: (args) => ({
    components: { Modal },
    setup() {
      return { args }
    },
    template: `
      <Modal v-bind="args">
        <p>Large modal content</p>
      </Modal>
    `
  })
}

export const WithFooter: Story = {
  args: {
    isOpen: true,
    title: 'Modal with Footer',
    size: 'md'
  },
  render: (args) => ({
    components: { Modal },
    setup() {
      return { args }
    },
    template: `
      <Modal v-bind="args">
        <p>Modal content</p>
        <template #footer>
          <button class="px-4 py-2 bg-primary-500 text-white rounded-md">Save</button>
          <button class="px-4 py-2 bg-neutral-200 rounded-md">Cancel</button>
        </template>
      </Modal>
    `
  })
}
