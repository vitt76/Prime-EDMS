<template>
  <Modal
    :is-open="true"
    title="Edit User"
    @close="$emit('close')"
    size="md"
  >
    <form v-if="user" class="edit-user-form">
      <div class="form-group">
        <Input
          v-model="formData.first_name"
          label="First Name"
          required
          :error="errors.first_name"
        />
      </div>

      <div class="form-group">
        <Input
          v-model="formData.last_name"
          label="Last Name"
          required
          :error="errors.last_name"
        />
      </div>

      <div class="form-group">
        <Input
          v-model="formData.email"
          type="email"
          label="Email"
          required
          :error="errors.email"
        />
      </div>

      <div class="form-group">
        <Select
          v-model="formData.role"
          :options="roleOptions"
          label="Role"
          required
          :error="errors.role"
        />
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input
            v-model="formData.is_active"
            type="checkbox"
            class="checkbox-input"
          />
          <span>Active</span>
        </label>
      </div>
    </form>

    <template #footer>
      <Button variant="ghost" @click="$emit('close')" type="button">
        Cancel
      </Button>
      <Button variant="primary" @click="handleSubmit" :loading="isSubmitting">
        Update User
      </Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { User, UpdateUserRequest } from '@/types/admin'
import Modal from '@/components/Common/Modal.vue'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import Button from '@/components/Common/Button.vue'

interface Props {
  user: User
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [data: UpdateUserRequest]
  close: []
}>()

const isSubmitting = ref(false)
const errors = reactive<Partial<Record<keyof UpdateUserRequest, string>>>({})

const formData = reactive<UpdateUserRequest>({
  first_name: props.user.first_name,
  last_name: props.user.last_name,
  email: props.user.email,
  role: props.user.role,
  is_active: props.user.is_active
})

const roleOptions = [
  { value: 'admin', label: 'Administrator' },
  { value: 'editor', label: 'Editor' },
  { value: 'viewer', label: 'Viewer' }
]

watch(
  () => props.user,
  (newUser) => {
    if (newUser) {
      formData.first_name = newUser.first_name
      formData.last_name = newUser.last_name
      formData.email = newUser.email
      formData.role = newUser.role
      formData.is_active = newUser.is_active
    }
  },
  { immediate: true }
)

const validate = (): boolean => {
  Object.keys(errors).forEach((key) => delete errors[key as keyof typeof errors])

  if (!formData.first_name?.trim()) {
    errors.first_name = 'First name is required'
  }

  if (!formData.last_name?.trim()) {
    errors.last_name = 'Last name is required'
  }

  if (!formData.email?.trim()) {
    errors.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'Invalid email format'
  }

  return Object.keys(errors).length === 0
}

const handleSubmit = async (): Promise<void> => {
  if (!validate()) return

  isSubmitting.value = true
  try {
    emit('submit', { ...formData })
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped lang="css">
.edit-user-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: var(--font-size-base, 14px);
  color: var(--color-text, #111827);
}

.checkbox-input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}
</style>

