<template>
  <Modal
    :is-open="true"
    title="Create Collection"
    @close="$emit('close')"
    size="md"
  >
    <form @submit.prevent="handleSubmit" class="create-collection-form">
      <div class="form-group">
        <Input
          v-model="formData.name"
          label="Collection Name"
          placeholder="e.g., Spring 2025 Campaign"
          required
          :error="errors.name"
          hint="1-255 characters"
          autocomplete="off"
        />
      </div>

      <div class="form-group">
        <label class="form-label">Description</label>
        <textarea
          v-model="formData.description"
          class="form-textarea"
          rows="3"
          placeholder="Optional description for this collection"
        />
      </div>

      <div class="form-group">
        <Select
          v-model="formData.visibility"
          :options="visibilityOptions"
          label="Visibility"
          required
          :error="errors.visibility"
        />
      </div>

      <div v-if="errorMessage" class="alert alert--error">
        <p>{{ errorMessage }}</p>
      </div>
    </form>

    <template #footer>
      <Button variant="ghost" @click="$emit('close')" type="button">
        Cancel
      </Button>
      <Button
        variant="primary"
        @click="handleSubmit"
        :loading="isSubmitting"
        type="submit"
      >
        Create Collection
      </Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { CreateCollectionRequest, CollectionVisibility } from '@/types/collections'
import Modal from '@/components/Common/Modal.vue'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import Button from '@/components/Common/Button.vue'

interface Props {
  parentId?: number | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [data: CreateCollectionRequest]
  close: []
}>()

const isSubmitting = ref(false)
const errorMessage = ref('')
const errors = reactive<{ name?: string; visibility?: string }>({})

const formData = reactive<{
  name: string
  description: string
  visibility: CollectionVisibility
}>({
  name: '',
  description: '',
  visibility: 'private'
})

const visibilityOptions = [
  { value: 'private', label: 'Private (only me)' },
  { value: 'shared', label: 'Shared (selected users)' },
  { value: 'public', label: 'Public (all users)' }
]

const validate = (): boolean => {
  Object.keys(errors).forEach((key) => delete errors[key as keyof typeof errors])
  errorMessage.value = ''

  if (!formData.name.trim()) {
    errors.name = 'Collection name is required'
    return false
  }

  if (formData.name.length > 255) {
    errors.name = 'Collection name must be 255 characters or less'
    return false
  }

  if (!formData.visibility) {
    errors.visibility = 'Visibility is required'
    return false
  }

  return true
}

const handleSubmit = (): void => {
  if (!validate()) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const data: CreateCollectionRequest = {
      name: formData.name.trim(),
      description: formData.description.trim() || undefined,
      parent_id: props.parentId || null,
      visibility: formData.visibility
    }

    emit('submit', data)
  } catch (error: any) {
    errorMessage.value = error.message || 'Failed to create collection'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped lang="css">
.create-collection-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: var(--font-size-sm, 12px);
  font-weight: 500;
  color: var(--color-text, #111827);
}

.form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 6px);
  font-size: var(--font-size-base, 14px);
  font-family: inherit;
  resize: vertical;
  transition: border-color 150ms ease;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.alert {
  padding: 12px;
  border-radius: var(--radius-base, 6px);
  font-size: var(--font-size-sm, 12px);
}

.alert--error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error, #ef4444);
  border: 1px solid rgba(239, 68, 68, 0.2);
}
</style>



