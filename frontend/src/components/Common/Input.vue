<template>
  <div class="w-full">
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-1">
      {{ label }}
      <span v-if="required" class="text-error">*</span>
    </label>
    <input
      :id="inputId"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :class="inputClasses"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @blur="$emit('blur', $event)"
      @focus="$emit('focus', $event)"
    />
    <p v-if="error" class="mt-1 text-sm text-error">{{ error }}</p>
    <p v-else-if="hint" class="mt-1 text-sm text-neutral-600 dark:text-neutral-600">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string | number
  type?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  error?: string
  hint?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false
})

defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const inputClasses = computed(() => {
  const base = 'w-full px-3 py-2 border rounded-base transition-all duration-fast focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed'
  
  if (props.error) {
    return `${base} border-error focus:ring-error focus:border-error`
  }
  
  return `${base} border-neutral-300 focus:ring-primary-500 focus:border-primary-500 dark:border-neutral-300 dark:bg-neutral-0 dark:text-neutral-900`
})
</script>


