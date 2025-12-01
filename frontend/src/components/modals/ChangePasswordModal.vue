<template>
  <Modal
    :isOpen="isOpen"
    title="Change password"
    size="md"
    @close="handleCancel"
  >
    <form class="change-password-modal" @submit.prevent="handleSave" novalidate>
      <Input
        id="old-password"
        label="Old password"
        type="password"
        placeholder="Enter current password"
        v-model="form.oldPassword"
        :error="errors.oldPassword"
        @blur="errors.oldPassword = validateOldPassword()"
        autocomplete="current-password"
        required
      />

      <Input
        id="new-password"
        label="New password"
        type="password"
        placeholder="Create a strong password"
        v-model="form.newPassword"
        :error="errors.newPassword"
        @input="onPasswordInput"
        autocomplete="new-password"
        required
      />

      <div class="change-password-modal__strength">
        <p class="change-password-modal__strength-label">
          Password strength: <strong :class="strengthClass">{{ strengthLabel }}</strong>
        </p>
        <div class="change-password-modal__strength-bar">
          <span
            v-for="segment in 3"
            :key="segment"
            class="change-password-modal__strength-segment"
            :class="{
              'change-password-modal__strength-segment--active': segment <= strengthSegments,
              'change-password-modal__strength-segment--strong': strengthLevel === 'strong'
            }"
          />
        </div>

        <ul class="change-password-modal__requirements">
          <li
            v-for="requirement in requirementList"
            :key="requirement.label"
            :class="{
              'change-password-modal__requirement--met': requirement.met
            }"
          >
            <i
              aria-hidden="true"
              :class="requirement.met ? 'icon icon-check' : 'icon icon-x'"
            />
            <span>{{ requirement.label }}</span>
          </li>
        </ul>
      </div>

      <Input
        id="confirm-password"
        label="Confirm password"
        type="password"
        placeholder="Repeat new password"
        v-model="form.confirmPassword"
        :error="errors.confirmPassword"
        @blur="errors.confirmPassword = validateConfirmPassword()"
        autocomplete="new-password"
        required
      />

      <p v-if="generalError" class="change-password-modal__error" role="alert">
        {{ generalError }}
      </p>
    </form>

    <template #footer>
      <Button variant="ghost" class="w-32" @click="handleCancel">
        Cancel
      </Button>
      <Button
        variant="primary"
        class="w-32"
        :loading="isSubmitting"
        :disabled="!canSave"
        @click="handleSave"
      >
        Save
      </Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import Input from '@/components/Common/Input.vue'
import { authService } from '@/services/authService'
import { useUIStore } from '@/stores/uiStore'
import { formatApiError } from '@/utils/errors'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  changed: []
}>()

const uiStore = useUIStore()

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const errors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const generalError = ref('')
const isSubmitting = ref(false)

const requirements = computed(() => {
  const password = form.newPassword
  return {
    length: password.length >= 12,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
  }
})

const requirementList = computed(() => [
  { label: 'At least 12 characters', met: requirements.value.length },
  { label: 'Uppercase letter', met: requirements.value.uppercase },
  { label: 'Lowercase letter', met: requirements.value.lowercase },
  { label: 'Number', met: requirements.value.number },
  { label: 'Special character', met: requirements.value.special }
])

const strengthLevel = computed<'weak' | 'fair' | 'strong'>(() => {
  const metCount = Object.values(requirements.value).filter(Boolean).length
  if (metCount >= 5) return 'strong'
  if (metCount >= 3) return 'fair'
  return 'weak'
})

const strengthLabel = computed(() => {
  switch (strengthLevel.value) {
    case 'strong':
      return 'Strong'
    case 'fair':
      return 'Fair'
    default:
      return 'Weak'
  }
})

const strengthClass = computed(() => `text-${strengthLevel.value === 'strong' ? 'emerald-500' : strengthLevel.value === 'fair' ? 'amber-500' : 'rose-500'}`)

const strengthSegments = computed(() => {
  const metCount = Object.values(requirements.value).filter(Boolean).length
  if (metCount >= 5) return 3
  if (metCount >= 3) return 2
  if (metCount >= 1) return 1
  return 0
})

const canSave = computed(() => {
  return (
    !isSubmitting.value &&
    !errors.oldPassword &&
    !errors.newPassword &&
    !errors.confirmPassword &&
    form.oldPassword.trim() !== '' &&
    form.newPassword.trim() !== '' &&
    form.confirmPassword.trim() !== '' &&
    strengthSegments.value === 3 &&
    form.newPassword === form.confirmPassword
  )
})

watch(
  () => form.newPassword,
  () => {
    errors.newPassword = validateNewPassword()
    errors.confirmPassword = validateConfirmPassword()
  }
)

watch(
  () => form.confirmPassword,
  () => {
    errors.confirmPassword = validateConfirmPassword()
  }
)

watch(
  () => props.isOpen,
  (open) => {
    if (!open) {
      resetForm()
    }
  }
)

function validateOldPassword(): string {
  if (!form.oldPassword.trim()) {
    return 'Old password is required.'
  }
  return ''
}

function validateNewPassword(): string {
  if (!form.newPassword.trim()) {
    return 'New password is required.'
  }
  if (strengthSegments.value < 3) {
    return 'Password must meet all strength requirements.'
  }
  return ''
}

function validateConfirmPassword(): string {
  if (!form.confirmPassword.trim()) {
    return 'Please confirm your new password.'
  }
  if (form.confirmPassword !== form.newPassword) {
    return 'Passwords do not match.'
  }
  return ''
}

function onPasswordInput(): void {
  errors.newPassword = validateNewPassword()
  errors.confirmPassword = validateConfirmPassword()
  generalError.value = ''
}

function resetForm(): void {
  form.oldPassword = ''
  form.newPassword = ''
  form.confirmPassword = ''
  errors.oldPassword = ''
  errors.newPassword = ''
  errors.confirmPassword = ''
  generalError.value = ''
  isSubmitting.value = false
}

async function handleSave(): Promise<void> {
  errors.oldPassword = validateOldPassword()
  errors.newPassword = validateNewPassword()
  errors.confirmPassword = validateConfirmPassword()

  if (errors.oldPassword || errors.newPassword || errors.confirmPassword) {
    generalError.value = 'Please resolve validation issues before saving.'
    return
  }

  if (!canSave.value) {
    return
  }

  isSubmitting.value = true
  generalError.value = ''

  try {
    await authService.changePassword({
      oldPassword: form.oldPassword,
      newPassword: form.newPassword
    })

    uiStore.addNotification({
      type: 'success',
      title: 'Password changed',
      message: 'Your password has been updated.'
    })
    emit('changed')
    handleCancel()
  } catch (error) {
    generalError.value = formatApiError(error)
  } finally {
    isSubmitting.value = false
  }
}

function handleCancel(): void {
  resetForm()
  emit('close')
}
</script>

<style scoped>
.change-password-modal {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

.change-password-modal__strength {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
}

.change-password-modal__strength-label {
  margin: 0;
  font-size: 0.9rem;
  color: #475569;
}

.change-password-modal__strength-bar {
  display: flex;
  height: 6px;
  margin: 0.5rem 0;
  gap: 0.25rem;
}

.change-password-modal__strength-segment {
  flex: 1;
  border-radius: 999px;
  background: #e2e8f0;
  transition: background 0.2s ease;
}

.change-password-modal__strength-segment--active {
  background: #f97316;
}

.change-password-modal__strength-segment--strong.change-password-modal__strength-segment--active {
  background: #22c55e;
}

.change-password-modal__requirements {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.change-password-modal__requirements li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #475569;
}

.change-password-modal__requirement--met {
  color: #16a34a;
}

.change-password-modal__error {
  color: #dc2626;
  font-size: 0.85rem;
  margin: 0;
}
</style>

