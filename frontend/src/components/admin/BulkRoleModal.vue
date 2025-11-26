<template>
  <Modal
    :is-open="true"
    title="Change Role for Selected Users"
    @close="$emit('close')"
    size="md"
  >
    <form class="bulk-role-form">
      <p class="bulk-role-form__info">
        Change role for {{ selectedCount }} selected user(s)
      </p>

      <div class="form-group">
        <Select
          v-model="selectedRole"
          :options="roleOptions"
          label="New Role"
          required
          :error="errors.role"
        />
      </div>
    </form>

    <template #footer>
      <Button variant="ghost" @click="$emit('close')" type="button">
        Cancel
      </Button>
      <Button variant="primary" @click="handleSubmit" :disabled="!selectedRole">
        Update Role
      </Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Select from '@/components/Common/Select.vue'
import Button from '@/components/Common/Button.vue'

interface Props {
  selectedCount: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [role: string]
  close: []
}>()

const selectedRole = ref<string>('')
const errors = reactive<{ role?: string }>({})

const roleOptions = [
  { value: 'admin', label: 'Administrator' },
  { value: 'editor', label: 'Editor' },
  { value: 'viewer', label: 'Viewer' }
]

const handleSubmit = (): void => {
  if (!selectedRole.value) {
    errors.role = 'Please select a role'
    return
  }

  emit('submit', selectedRole.value)
}
</script>

<style scoped lang="css">
.bulk-role-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bulk-role-form__info {
  font-size: var(--font-size-base, 14px);
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 8px;
}

.form-group {
  display: flex;
  flex-direction: column;
}
</style>

