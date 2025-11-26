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

        <button type="submit" class="auth-form__submit" :disabled="isSubmitting || success">
          <span v-if="success">Password updated! Redirecting…</span>
          <span v-else>Save new password</span>
        </button>
      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/authService'
import { formatApiError } from '@/utils/errors'
import { useUIStore } from '@/stores/uiStore'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()

const newPassword = ref('')
const confirmPassword = ref('')
const passwordError = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)
const success = ref(false)
const tokenError = ref('')
const token = ref<string | null>(null)

watchEffect(() => {
  const queryToken = route.query.token
  token.value = typeof queryToken === 'string' ? queryToken : null
  if (!token.value) {
    tokenError.value = 'Reset token is missing. Please request a new link.'
  } else {
    tokenError.value = ''
  }
})

const validatePasswords = (): boolean => {
  passwordError.value = ''
  if (!newPassword.value || newPassword.value.length < 8) {
    passwordError.value = 'Password must be at least 8 characters.'
    return false
  }
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'Passwords do not match.'
    return false
  }
  return true
}

const handleSubmit = async (): Promise<void> => {
  if (!token.value || !validatePasswords()) {
    return
  }
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    await authService.resetPassword({
      token: token.value,
      newPassword: newPassword.value,
      confirmPassword: confirmPassword.value
    })
    success.value = true
    uiStore.addNotification({
      type: 'success',
      title: 'Password reset',
      message: 'Your password has been updated. Redirecting to login.'
    })
    setTimeout(() => {
      router.push({ name: 'login', query: { resetSuccess: 'true' } })
    }, 1200)
  } catch (err) {
    errorMessage.value = formatApiError(err)
  } finally {
    isSubmitting.value = false
  }
}
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
  max-width: 460px;
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
  margin: 0 0 20px;
  color: #4b5563;
}

.auth-link {
  display: inline-block;
  margin-top: 4px;
  color: var(--color-primary, #2563eb);
  text-decoration: underline;
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
  margin: 2px 0 4px;
}

.auth-form__error {
  color: #dc2626;
  font-size: 0.875rem;
}

.auth-form__error--global {
  margin-bottom: 12px;
}

.auth-form__submit {
  margin-top: 12px;
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
</style>
<template>
  <div class="auth-page">
    <div class="auth-page__container">
      <div class="auth-page__header">
        <h1 class="auth-page__title">Reset Password</h1>
        <p v-if="!tokenValid" class="auth-page__subtitle">
          This reset link is invalid or has expired.
        </p>
        <p v-else class="auth-page__subtitle">
          Enter your new password below
        </p>
      </div>

      <div v-if="!tokenValid" class="auth-page__invalid-token">
        <p class="invalid-token__message">
          The password reset link is invalid or has expired. Please request a new one.
        </p>
        <Button variant="primary" @click="handleRequestNewLink">
          Request New Link
        </Button>
      </div>

      <form v-else @submit.prevent="handleSubmit" class="auth-page__form">
        <div class="form-group">
          <Input
            v-model="password"
            type="password"
            label="New Password"
            placeholder="Enter new password"
            required
            :error="errors.password"
            :disabled="isSubmitting"
            autocomplete="new-password"
            @input="checkPasswordStrength"
          />
        </div>

        <div v-if="password" class="password-strength">
          <div class="password-strength__indicator">
            <div
              :class="[
                'password-strength__bar',
                `password-strength__bar--${passwordStrength}`
              ]"
              :style="{ width: `${passwordStrengthPercent}%` }"
            />
          </div>
          <p class="password-strength__label">
            Strength: {{ passwordStrengthLabel }}
          </p>
        </div>

        <div v-if="password" class="password-requirements">
          <p class="password-requirements__title">Password must contain:</p>
          <ul class="password-requirements__list">
            <li
              :class="[
                'password-requirements__item',
                {
                  'password-requirements__item--met': passwordMeets.length >= 8
                }
              ]"
            >
              At least 8 characters
            </li>
            <li
              :class="[
                'password-requirements__item',
                {
                  'password-requirements__item--met': passwordMeets.uppercase
                }
              ]"
            >
              One uppercase letter
            </li>
            <li
              :class="[
                'password-requirements__item',
                {
                  'password-requirements__item--met': passwordMeets.lowercase
                }
              ]"
            >
              One lowercase letter
            </li>
            <li
              :class="[
                'password-requirements__item',
                {
                  'password-requirements__item--met': passwordMeets.number
                }
              ]"
            >
              One number
            </li>
            <li
              :class="[
                'password-requirements__item',
                {
                  'password-requirements__item--met': passwordMeets.special
                }
              ]"
            >
              One special character
            </li>
          </ul>
        </div>

        <div class="form-group">
          <Input
            v-model="passwordConfirm"
            type="password"
            label="Confirm Password"
            placeholder="Confirm new password"
            required
            :error="errors.password_confirm"
            :disabled="isSubmitting"
            autocomplete="new-password"
          />
        </div>

        <div v-if="errorMessage" class="alert alert--error">
          <p>{{ errorMessage }}</p>
        </div>

        <Button
          type="submit"
          variant="primary"
          :loading="isSubmitting"
          :disabled="!isFormValid"
          class="auth-page__submit"
        >
          Reset Password
        </Button>
      </form>

      <div class="auth-page__footer">
        <p class="auth-page__footer-text">
          Remember your password?
          <router-link to="/login" class="auth-page__link">
            Back to Login
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from '@/services/authService'
import Input from '@/components/Common/Input.vue'
import Button from '@/components/Common/Button.vue'

const router = useRouter()
const route = useRoute()

const token = computed(() => route.params.token as string)
const password = ref('')
const passwordConfirm = ref('')
const isSubmitting = ref(false)
const tokenValid = ref(false)
const isValidatingToken = ref(true)
const errorMessage = ref('')
const errors = reactive<{ password?: string; password_confirm?: string }>({})

const passwordMeets = reactive({
  length: false,
  uppercase: false,
  lowercase: false,
  number: false,
  special: false
})

const passwordStrength = computed<'weak' | 'medium' | 'strong'>(() => {
  const metCount = Object.values(passwordMeets).filter(Boolean).length
  if (metCount < 3) return 'weak'
  if (metCount < 5) return 'medium'
  return 'strong'
})

const passwordStrengthPercent = computed(() => {
  const metCount = Object.values(passwordMeets).filter(Boolean).length
  return (metCount / 5) * 100
})

const passwordStrengthLabel = computed(() => {
  return passwordStrength.value.charAt(0).toUpperCase() + passwordStrength.value.slice(1)
})

const isFormValid = computed(() => {
  return (
    password.value.length >= 8 &&
    passwordMeets.uppercase &&
    passwordMeets.lowercase &&
    passwordMeets.number &&
    passwordMeets.special &&
    password.value === passwordConfirm.value
  )
})

const checkPasswordStrength = (): void => {
  passwordMeets.length = password.value.length >= 8
  passwordMeets.uppercase = /[A-Z]/.test(password.value)
  passwordMeets.lowercase = /[a-z]/.test(password.value)
  passwordMeets.number = /[0-9]/.test(password.value)
  passwordMeets.special = /[^A-Za-z0-9]/.test(password.value)
}

const validateToken = async (): Promise<void> => {
  isValidatingToken.value = true
  try {
    await authService.validateResetToken(token.value)
    tokenValid.value = true
  } catch (error: any) {
    tokenValid.value = false
    if (error.response?.status === 400 || error.response?.status === 404) {
      errorMessage.value = 'This reset link is invalid or has expired.'
    }
  } finally {
    isValidatingToken.value = false
  }
}

const validate = (): boolean => {
  Object.keys(errors).forEach((key) => delete errors[key as keyof typeof errors])
  errorMessage.value = ''

  if (!password.value) {
    errors.password = 'Password is required'
    return false
  }

  if (password.value.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    return false
  }

  if (!passwordMeets.uppercase || !passwordMeets.lowercase || !passwordMeets.number || !passwordMeets.special) {
    errors.password = 'Password does not meet requirements'
    return false
  }

  if (!passwordConfirm.value) {
    errors.password_confirm = 'Please confirm your password'
    return false
  }

  if (password.value !== passwordConfirm.value) {
    errors.password_confirm = 'Passwords do not match'
    return false
  }

  return true
}

const handleSubmit = async (): Promise<void> => {
  if (!validate()) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    await authService.resetPassword(token.value, password.value, passwordConfirm.value)
    // Redirect to login with success message
    router.push({
      name: 'login',
      query: { message: 'Password reset successfully. Please log in with your new password.' }
    })
  } catch (error: any) {
    if (error.response?.status === 400) {
      errorMessage.value = error.response.data?.message || 'Invalid request. Please check your input.'
    } else if (error.response?.status === 404) {
      errorMessage.value = 'This reset link is invalid or has expired.'
      tokenValid.value = false
    } else {
      errorMessage.value = 'An error occurred. Please try again.'
    }
  } finally {
    isSubmitting.value = false
  }
}

const handleRequestNewLink = (): void => {
  router.push({ name: 'forgot-password' })
}

onMounted(async () => {
  if (token.value) {
    await validateToken()
  } else {
    tokenValid.value = false
    isValidatingToken.value = false
  }
})
</script>

<style scoped lang="css">
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--color-bg-1, #f9fafb);
}

.auth-page__container {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface, #ffffff);
  border-radius: var(--radius-lg, 8px);
  padding: 32px;
  box-shadow: var(--shadow-md, 0 4px 6px rgba(0, 0, 0, 0.1));
}

.auth-page__header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-page__title {
  font-size: var(--font-size-2xl, 24px);
  font-weight: 600;
  color: var(--color-text, #111827);
  margin-bottom: 8px;
}

.auth-page__subtitle {
  font-size: var(--font-size-base, 14px);
  color: var(--color-text-secondary, #6b7280);
  line-height: 1.5;
}

.auth-page__invalid-token {
  text-align: center;
  padding: 24px;
}

.invalid-token__message {
  font-size: var(--font-size-base, 14px);
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 16px;
}

.auth-page__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.password-strength {
  margin-top: -8px;
}

.password-strength__indicator {
  height: 4px;
  background: var(--color-border, #e5e7eb);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.password-strength__bar {
  height: 100%;
  transition: width 200ms ease, background-color 200ms ease;
}

.password-strength__bar--weak {
  background: var(--color-error, #ef4444);
}

.password-strength__bar--medium {
  background: var(--color-warning, #f59e0b);
}

.password-strength__bar--strong {
  background: var(--color-success, #10b981);
}

.password-strength__label {
  font-size: var(--font-size-xs, 11px);
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

.password-requirements {
  padding: 12px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 6px);
}

.password-requirements__title {
  font-size: var(--font-size-sm, 12px);
  font-weight: 500;
  color: var(--color-text, #111827);
  margin-bottom: 8px;
}

.password-requirements__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.password-requirements__item {
  font-size: var(--font-size-xs, 11px);
  color: var(--color-text-secondary, #6b7280);
  padding-left: 20px;
  position: relative;
}

.password-requirements__item::before {
  content: '✗';
  position: absolute;
  left: 0;
  color: var(--color-error, #ef4444);
}

.password-requirements__item--met {
  color: var(--color-success, #10b981);
}

.password-requirements__item--met::before {
  content: '✓';
  color: var(--color-success, #10b981);
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

.auth-page__submit {
  width: 100%;
  margin-top: 8px;
}

.auth-page__footer {
  margin-top: 24px;
  text-align: center;
}

.auth-page__footer-text {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
}

.auth-page__link {
  color: var(--color-primary, #3b82f6);
  text-decoration: none;
  font-weight: 500;
}

.auth-page__link:hover {
  text-decoration: underline;
}
</style>



