import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import Modal from './Modal.vue'
import Button from './Button.vue'

const meta: Meta<typeof Modal> = {
  title: 'Common/Modal',
  component: Modal,
  tags: ['autodocs']
}

export default meta
type Story = StoryObj<typeof Modal>

export const Default: Story = {
  render: () => {
    const isOpen = ref(false)
    return {
      components: { Modal, Button },
      setup() {
        return { isOpen }
      },
      template: `
        <div>
          <Button @click="isOpen = true">Open Modal</Button>
          <Modal v-model:is-open="isOpen" title="Example Modal">
            <p>This is modal content. You can add any content here.</p>
            <template #footer>
              <Button variant="secondary" @click="isOpen = false">Cancel</Button>
              <Button variant="primary" @click="isOpen = false">Confirm</Button>
            </template>
          </Modal>
        </div>
      `
    }
  }
}

export const Small: Story = {
  render: () => {
    const isOpen = ref(false)
    return {
      components: { Modal, Button },
      setup() {
        return { isOpen }
      },
      template: `
        <div>
          <Button @click="isOpen = true">Open Small Modal</Button>
          <Modal v-model:is-open="isOpen" title="Small Modal" size="sm">
            <p>This is a small modal.</p>
          </Modal>
        </div>
      `
    }
  }
}

export const Large: Story = {
  render: () => {
    const isOpen = ref(false)
    return {
      components: { Modal, Button },
      setup() {
        return { isOpen }
      },
      template: `
        <div>
          <Button @click="isOpen = true">Open Large Modal</Button>
          <Modal v-model:is-open="isOpen" title="Large Modal" size="lg">
            <p>This is a large modal with more space for content.</p>
          </Modal>
        </div>
      `
    }
  }
}


