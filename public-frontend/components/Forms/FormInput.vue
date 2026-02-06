<template>
  <div class="space-y-1.5">
    <!-- Label -->
    <label 
      :for="inputId"
      class="flex items-center gap-1 text-sm font-medium text-neutral-700"
    >
      {{ label }}
      <span 
        v-if="required" 
        class="text-error" 
        aria-hidden="true"
      >*</span>
      <span v-if="required" class="sr-only">(required)</span>
    </label>

    <!-- Input Container -->
    <div class="relative">
      <!-- Leading Icon -->
      <div 
        v-if="leadingIcon" 
        class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2"
      >
        <component :is="leadingIcon" class="h-5 w-5 text-neutral-400" />
      </div>

      <!-- Input -->
      <input
        :id="inputId"
        :type="inputType"
        :name="name"
        :value="modelValue"
        :required="required"
        :disabled="disabled"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        :aria-invalid="!!error"
        :aria-describedby="ariaDescribedBy"
        class="w-full rounded-lg border px-3 py-2.5 text-sm transition duration-150 focus:outline-none focus:ring-2 disabled:cursor-not-allowed disabled:bg-neutral-50 disabled:text-neutral-500"
        :class="[
          error 
            ? 'border-error focus:border-error focus:ring-error/20' 
            : 'border-neutral-200 focus:border-primary-500 focus:ring-primary-500/20',
          leadingIcon ? 'pl-10' : '',
          trailingIcon || showValidation ? 'pr-10' : ''
        ]"
        @input="handleInput"
        @blur="touched = true"
      />

      <!-- Trailing Icon / Validation Icons -->
      <div 
        class="absolute right-3 top-1/2 -translate-y-1/2"
      >
        <!-- Password Toggle -->
        <button 
          v-if="type === 'password'" 
          type="button"
          class="text-neutral-400 hover:text-neutral-600"
          @click="togglePasswordVisibility"
          :aria-label="showPassword ? 'Hide password' : 'Show password'"
        >
          <EyeSlashIcon v-if="showPassword" class="h-5 w-5" />
          <EyeIcon v-else class="h-5 w-5" />
        </button>

        <!-- Validation Icons -->
        <template v-else-if="showValidation && touched">
          <CheckCircleIcon 
            v-if="isValid && modelValue" 
            class="h-5 w-5 text-success" 
            aria-hidden="true"
          />
          <ExclamationCircleIcon 
            v-else-if="error" 
            class="h-5 w-5 text-error" 
            aria-hidden="true"
          />
        </template>

        <!-- Custom Trailing Icon -->
        <component 
          v-else-if="trailingIcon" 
          :is="trailingIcon" 
          class="h-5 w-5 text-neutral-400" 
        />
      </div>
    </div>

    <!-- Error Message -->
    <p 
      v-if="error" 
      :id="`${inputId}-error`" 
      class="flex items-center gap-1 text-xs text-error"
      role="alert"
    >
      <ExclamationCircleIcon class="h-3.5 w-3.5" />
      {{ error }}
    </p>

    <!-- Hint Text -->
    <p 
      v-else-if="hint" 
      :id="`${inputId}-hint`" 
      class="text-xs text-neutral-500"
    >
      {{ hint }}
    </p>

    <!-- Character Counter -->
    <p 
      v-if="maxLength && showCharCount" 
      class="text-right text-xs text-neutral-400"
      :class="{ 'text-error': (modelValue?.length || 0) > maxLength }"
    >
      {{ modelValue?.length || 0 }} / {{ maxLength }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/vue/24/solid'
import type { Component } from 'vue'
import { debounce } from '~/utils/helpers'

const props = withDefaults(
  defineProps<{
    label: string
    name: string
    type?: string
    modelValue?: string
    error?: string
    required?: boolean
    disabled?: boolean
    placeholder?: string
    hint?: string
    autocomplete?: string
    showValidation?: boolean
    validateOnInput?: boolean
    leadingIcon?: Component
    trailingIcon?: Component
    maxLength?: number
    showCharCount?: boolean
  }>(),
  {
    type: 'text',
    showValidation: true,
    showCharCount: false,
    validateOnInput: false
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'validate', value: string): void
}>()

// Generate unique ID for accessibility
const inputId = computed(() => `input-${props.name}-${Math.random().toString(36).slice(2, 9)}`)

// Track if field has been touched (for validation display)
const touched = ref(false)

// Password visibility toggle
const showPassword = ref(false)
const inputType = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'text' : 'password'
  }
  return props.type
})

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// Compute isValid (absence of error when there's a value)
const isValid = computed(() => !props.error && props.modelValue)

// Compute aria-describedby
const ariaDescribedBy = computed(() => {
  const ids: string[] = []
  if (props.error) ids.push(`${inputId.value}-error`)
  else if (props.hint) ids.push(`${inputId.value}-hint`)
  return ids.length ? ids.join(' ') : undefined
})

// Handle input
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const validateInput = debounce(() => {
  if (props.validateOnInput) {
    emit('validate', props.modelValue || '')
  }
}, 300)

watch(
  () => props.modelValue,
  () => {
    if (props.validateOnInput) {
      validateInput()
    }
  }
)
</script>
