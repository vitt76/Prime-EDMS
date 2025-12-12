// @ts-nocheck
<template>
  <div class="auth-page">
    <main class="auth-card" role="main" aria-labelledby="reset-password-title">
      <h1 id="reset-password-title" class="auth-card__title">Reset password</h1>
      <p class="auth-card__description">
        Choose a new password to continue. Password must be at least 8 characters long.
      </p>

      <div v-if="tokenError" class="auth-form__error auth-form__error--global">
        {{ tokenError }}
        <router-link to="/auth/forgot-password" class="auth-link">
          Request a new reset link
        </router-link>
      </div>

      <form v-else class="auth-form" @submit.prevent="handleSubmit" novalidate>
        <label for="password" class="auth-form__label">
          New password
          <span class="auth-form__required">*</span>
        </label>
        <input
          id="password"
          type="password"
          v-model="newPassword"
          class="auth-form__input"
          :disabled="isSubmitting || success"
          autocomplete="new-password"
          aria-describedby="password-help"
        />
        <p id="password-help" class="auth-form__helper">
          Minimum 8 characters.
        </p>

        <label for="confirm-password" class="auth-form__label">
          Confirm password
          <span class="auth-form__required">*</span>
        </label>
        <input
          id="confirm-password"
          type="password"
          v-model="confirmPassword"
          class="auth-form__input"
          :disabled="isSubmitting || success"
          autocomplete="new-password"
        />
        <p v-if="passwordError" class="auth-form__error">{{ passwordError }}</p>

        <div v-if="errorMessage" class="auth-form__error auth-form__error--global">
          {{ errorMessage }}
        </div>

        <div v-if="success" class="auth-form__success auth-form__success--global">
          Password reset successfully! Redirecting to login...
        </div>

        <button
          type="submit"
          class="auth-form__submit"
          :disabled="isSubmitting || success"
          aria-live="polite"
        >
          <span v-if="isSubmitting">Resetting password...</span>
          <span v-else-if="success">Success!</span>
          <span v-else>Reset password</span>
        </button>
      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/authService'
import { formatApiError } from '@/utils/errors'

const route = useRoute()
const router = useRouter()

const newPassword = ref('')
const confirmPassword = ref('')
const passwordError = ref('')
const errorMessage = ref('')
const tokenError = ref('')
const isSubmitting = ref(false)
const success = ref(false)
let redirectTimer: ReturnType<typeof setTimeout> | null = null

const validatePasswords = (): boolean => {
  passwordError.value = ''
  errorMessage.value = ''

  if (!newPassword.value) {
    passwordError.value = 'Password is required'
    return false
  }

  if (newPassword.value.length < 8) {
    passwordError.value = 'Password must be at least 8 characters long'
    return false
  }

  if (!confirmPassword.value) {
    passwordError.value = 'Please confirm your password'
    return false
  }

  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'Passwords do not match'
    return false
  }

  return true
}

const handleSubmit = async (): Promise<void> => {
  if (!validatePasswords()) {
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = route.params.token as string
    if (!token) {
      tokenError.value = 'Invalid reset link'
      return
    }

    await authService.resetPassword(token, newPassword.value)
    success.value = true

    // Redirect to login after success
    redirectTimer = setTimeout(() => {
      router.push('/auth/login')
    }, 3000)

  } catch (err) {
    errorMessage.value = formatApiError(err)
  } finally {
    isSubmitting.value = false
  }
}

onBeforeUnmount(() => {
  if (redirectTimer) {
    clearTimeout(redirectTimer)
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background, #f5f5f5);
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.1);
}

.auth-card__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 600;
}

.auth-card__description {
  margin: 0 0 24px;
  color: #4b5563;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auth-form__label {
  font-weight: 500;
}

.auth-form__required {
  color: #ef4444;
  margin-left: 4px;
}

.auth-form__input {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 1rem;
}

.auth-form__helper {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 4px 0 0;
}

.auth-form__error {
  color: #dc2626;
  font-size: 0.875rem;
}

.auth-form__error--global {
  margin-top: 12px;
}

.auth-form__success {
  color: #16a34a;
  font-weight: 500;
}

.auth-form__success--global {
  margin-top: 16px;
  text-align: center;
}

.auth-form__submit {
  margin-top: 16px;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: var(--color-primary, #2563eb);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.auth-form__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-link {
  display: block;
  margin-top: 8px;
  color: var(--color-primary, #2563eb);
  text-decoration: none;
  font-size: 0.875rem;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>