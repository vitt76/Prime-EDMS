<template>
  <Modal
    :is-open="true"
    :title="title"
    @close="$emit('cancel')"
    size="md"
  >
    <div class="delete-confirm">
      <div class="delete-confirm__icon">
        <svg
          class="w-12 h-12 text-error"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <p class="delete-confirm__message">{{ message }}</p>
    </div>

    <template #footer>
      <Button variant="ghost" @click="$emit('cancel')" type="button">
        Cancel
      </Button>
      <Button variant="danger" @click="$emit('confirm')" type="button">
        Delete
      </Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'

interface Props {
  title: string
  message: string
}

defineProps<Props>()

defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<style scoped lang="css">
.delete-confirm {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px;
  text-align: center;
}

.delete-confirm__icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-confirm__message {
  font-size: var(--font-size-base, 14px);
  color: var(--color-text, #111827);
  line-height: 1.5;
}
</style>



