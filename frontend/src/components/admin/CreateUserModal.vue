<template>
  <Modal :is-open="true" title="Create User" @close="$emit('close')" size="md">
    <form class="create-user-form">
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
          v-model="formData.username"
          label="Username"
          required
          :error="errors.username"
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
        <Input
          v-model="formData.password"
          type="password"
          label="Password"
          :required="!formData.send_invitation"
          :error="errors.password"
          hint="Leave empty to send invitation email"
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

      <div class="form-group">
        <label class="checkbox-label">
          <input
            v-model="formData.send_invitation"
            type="checkbox"
            class="checkbox-input"
          />
          <span>Send invitation email</span>
        </label>
      </div>
    </form>

    <template #footer>
      <Button variant="ghost" @click="$emit('close')" type="button">
        Cancel
      </Button>
      <Button variant="primary" @click="handleSubmit" :loading="isSubmitting">
        Create User
      </Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { CreateUserRequest } from '@/types/admin'
import Modal from '@/components/Common/Modal.vue'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import Button from '@/components/Common/Button.vue'

const emit = defineEmits<{
  submit: [data: CreateUserRequest]
  close: []
}>()

const isSubmitting = ref(false)
const errors = reactive<Partial<Record<keyof CreateUserRequest, string>>>({})

const formData = reactive<CreateUserRequest & { send_invitation: boolean }>({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  role: 'viewer',
  is_active: true,
  send_invitation: false
})

const roleOptions = [
  { value: 'admin', label: 'Administrator' },
  { value: 'editor', label: 'Editor' },
  { value: 'viewer', label: 'Viewer' }
]

const validate = (): boolean => {
  Object.keys(errors).forEach((key) => delete errors[key as keyof typeof errors])

  if (!formData.first_name.trim()) {
    errors.first_name = 'First name is required'
  }

  if (!formData.last_name.trim()) {
    errors.last_name = 'Last name is required'
  }

  if (!formData.username.trim()) {
    errors.username = 'Username is required'
  }

  if (!formData.email.trim()) {
    errors.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'Invalid email format'
  }

  if (!formData.send_invitation && !formData.password) {
    errors.password = 'Password is required if not sending invitation'
  }

  return Object.keys(errors).length === 0
}

const handleSubmit = async (): Promise<void> => {
  if (!validate()) return

  isSubmitting.value = true
  try {
    const submitData: CreateUserRequest = {
      ...formData,
      password: formData.send_invitation ? undefined : formData.password
    }
    emit('submit', submitData)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped lang="css">
.create-user-form {
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

