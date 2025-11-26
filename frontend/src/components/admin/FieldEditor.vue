<template>
  <div class="field-editor">
    <div class="field-editor__header">
      <h3 class="field-editor__title">
        {{ editingField ? 'Edit Field' : 'Add Field' }}
      </h3>
      <Button
        v-if="editingField"
        variant="ghost"
        size="sm"
        @click="$emit('cancel')"
        aria-label="Cancel editing"
      >
        Cancel
      </Button>
    </div>

    <form @submit.prevent="handleSave" class="field-editor__form">
      <!-- Field Name -->
      <div class="form-group">
        <Input
          v-model="formData.name"
          label="Field Name"
          placeholder="e.g., photographer_name"
          required
          :error="errors.name"
          hint="Must be unique and valid identifier (letters, numbers, underscore)"
        />
      </div>

      <!-- Field Label -->
      <div class="form-group">
        <Input
          v-model="formData.label"
          label="Field Label"
          placeholder="e.g., Photographer Name"
          required
          :error="errors.label"
          hint="Display name for users"
        />
      </div>

      <!-- Field Type -->
      <div class="form-group">
        <Select
          v-model="formData.type"
          :options="fieldTypeOptions"
          label="Field Type"
          required
          :error="errors.type"
          @change="handleTypeChange"
        />
      </div>

      <!-- Description -->
      <div class="form-group">
        <label class="form-label">Description</label>
        <textarea
          v-model="formData.description"
          class="form-textarea"
          rows="3"
          placeholder="Optional description for this field"
        />
      </div>

      <!-- Required -->
      <div class="form-group">
        <label class="checkbox-label">
          <input
            v-model="formData.required"
            type="checkbox"
            class="checkbox-input"
          />
          <span>Required field</span>
        </label>
      </div>

      <!-- Default Value (conditional based on type) -->
      <div v-if="showDefaultValue" class="form-group">
        <Input
          v-model="defaultValueString"
          :label="`Default Value (${formData.type})`"
          :type="getDefaultValueInputType()"
          :error="errors.default_value"
          :hint="getDefaultValueHint()"
        />
      </div>

      <!-- Options (for select/multi_select) -->
      <div v-if="needsOptions" class="form-group">
        <label class="form-label">Options</label>
        <div class="options-list">
          <div
            v-for="(option, index) in formData.options"
            :key="index"
            class="options-list__item"
          >
            <Input
              v-model="formData.options[index]"
              :placeholder="`Option ${index + 1}`"
              @blur="validateOptions"
            />
            <Button
              variant="ghost"
              size="sm"
              @click="removeOption(index)"
              aria-label="Remove option"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </Button>
          </div>
          <Button
            variant="secondary"
            size="sm"
            @click="addOption"
            type="button"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            Add Option
          </Button>
        </div>
        <p v-if="errors.options" class="form-error">{{ errors.options }}</p>
      </div>

      <!-- Validation Rules -->
      <div class="form-group">
        <label class="form-label">Validation Rules</label>
        <div class="validation-rules">
          <!-- Min/Max Length (for text) -->
          <div v-if="supportsLengthValidation" class="validation-rules__row">
            <Input
              v-model.number="formData.validation_rules.min_length"
              type="number"
              label="Min Length"
              placeholder="0"
            />
            <Input
              v-model.number="formData.validation_rules.max_length"
              type="number"
              label="Max Length"
              placeholder="255"
            />
          </div>

          <!-- Min/Max Value (for number) -->
          <div v-if="supportsValueValidation" class="validation-rules__row">
            <Input
              v-model.number="formData.validation_rules.min_value"
              type="number"
              label="Min Value"
              placeholder="0"
            />
            <Input
              v-model.number="formData.validation_rules.max_value"
              type="number"
              label="Max Value"
              placeholder="100"
            />
          </div>

          <!-- Pattern (for text) -->
          <div v-if="supportsPatternValidation" class="form-group">
            <Input
              v-model="formData.validation_rules.pattern"
              label="Pattern (Regex)"
              placeholder="e.g., ^[A-Z]+$"
              :error="errors.pattern"
              hint="Regular expression for validation"
            />
          </div>
        </div>
      </div>

      <!-- Help Text -->
      <div class="form-group">
        <Input
          v-model="formData.help_text"
          label="Help Text"
          placeholder="Optional help text shown to users"
          hint="Displayed below the field in forms"
        />
      </div>

      <!-- Placeholder -->
      <div class="form-group">
        <Input
          v-model="formData.placeholder"
          label="Placeholder"
          placeholder="e.g., Enter photographer name"
          hint="Placeholder text for input field"
        />
      </div>

      <!-- Actions -->
      <div class="field-editor__actions">
        <Button variant="ghost" @click="$emit('cancel')" type="button">
          Cancel
        </Button>
        <Button variant="primary" type="submit" :loading="isSaving">
          {{ editingField ? 'Update Field' : 'Add Field' }}
        </Button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { SchemaField, FieldType } from '@/types/admin'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import Button from '@/components/Common/Button.vue'

interface Props {
  field?: SchemaField | null
  existingFieldNames?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  field: null,
  existingFieldNames: () => []
})

const emit = defineEmits<{
  save: [field: SchemaField]
  cancel: []
}>()

const isSaving = ref(false)
const errors = reactive<Partial<Record<keyof SchemaField, string>>>({})

const editingField = computed(() => props.field !== null)

const formData = reactive<SchemaField>({
  name: props.field?.name || '',
  label: props.field?.label || '',
  type: props.field?.type || 'text',
  description: props.field?.description || '',
  required: props.field?.required || false,
  default_value: props.field?.default_value,
  options: props.field?.options ? [...props.field.options] : [],
  validation_rules: props.field?.validation_rules || {},
  placeholder: props.field?.placeholder || '',
  help_text: props.field?.help_text || ''
})

const defaultValueString = ref(
  props.field?.default_value !== undefined
    ? String(props.field.default_value)
    : ''
)

const fieldTypeOptions = [
  { value: 'text', label: 'Text (single line)' },
  { value: 'textarea', label: 'Text Area (multi-line)' },
  { value: 'number', label: 'Number' },
  { value: 'date', label: 'Date' },
  { value: 'date_range', label: 'Date Range' },
  { value: 'select', label: 'Select (dropdown)' },
  { value: 'multi_select', label: 'Multi-select' },
  { value: 'checkbox', label: 'Checkbox' },
  { value: 'file_upload', label: 'File Upload' },
  { value: 'url', label: 'URL' }
]

const needsOptions = computed(() => {
  return formData.type === 'select' || formData.type === 'multi_select'
})

const showDefaultValue = computed(() => {
  return formData.type !== 'file_upload'
})

const supportsLengthValidation = computed(() => {
  return formData.type === 'text' || formData.type === 'textarea' || formData.type === 'url'
})

const supportsValueValidation = computed(() => {
  return formData.type === 'number'
})

const supportsPatternValidation = computed(() => {
  return formData.type === 'text' || formData.type === 'url'
})

// Watch for field changes
watch(
  () => props.field,
  (newField) => {
    if (newField) {
      formData.name = newField.name
      formData.label = newField.label
      formData.type = newField.type
      formData.description = newField.description || ''
      formData.required = newField.required
      formData.default_value = newField.default_value
      formData.options = newField.options ? [...newField.options] : []
      formData.validation_rules = newField.validation_rules || {}
      formData.placeholder = newField.placeholder || ''
      formData.help_text = newField.help_text || ''
      defaultValueString.value =
        newField.default_value !== undefined
          ? String(newField.default_value)
          : ''
    } else {
      // Reset form
      formData.name = ''
      formData.label = ''
      formData.type = 'text'
      formData.description = ''
      formData.required = false
      formData.default_value = undefined
      formData.options = []
      formData.validation_rules = {}
      formData.placeholder = ''
      formData.help_text = ''
      defaultValueString.value = ''
    }
  },
  { immediate: true }
)

const handleTypeChange = (): void => {
  // Reset options if type changed away from select/multi_select
  if (!needsOptions.value) {
    formData.options = []
  }
  // Reset validation rules if type changed
  if (!supportsLengthValidation.value && !supportsValueValidation.value) {
    formData.validation_rules = {}
  }
}

const addOption = (): void => {
  if (!formData.options) {
    formData.options = []
  }
  formData.options.push('')
}

const removeOption = (index: number): void => {
  if (formData.options) {
    formData.options.splice(index, 1)
  }
}

const validateOptions = (): void => {
  if (needsOptions.value) {
    const validOptions = formData.options?.filter((opt) => opt.trim() !== '') || []
    if (validOptions.length === 0) {
      errors.options = 'At least one option is required for select/multi-select fields'
    } else {
      delete errors.options
    }
  }
}

const getDefaultValueInputType = (): string => {
  switch (formData.type) {
    case 'number':
      return 'number'
    case 'date':
      return 'date'
    case 'url':
      return 'url'
    default:
      return 'text'
  }
}

const getDefaultValueHint = (): string => {
  switch (formData.type) {
    case 'number':
      return 'Numeric default value'
    case 'date':
      return 'Date in YYYY-MM-DD format'
    case 'url':
      return 'Valid URL'
    default:
      return 'Default text value'
  }
}

const validate = (): boolean => {
  Object.keys(errors).forEach((key) => delete errors[key as keyof typeof errors])

  // Name validation
  if (!formData.name.trim()) {
    errors.name = 'Field name is required'
  } else if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(formData.name)) {
    errors.name = 'Field name must be a valid identifier (letters, numbers, underscore, start with letter)'
  } else if (
    props.existingFieldNames.includes(formData.name) &&
    (!editingField.value || props.field?.name !== formData.name)
  ) {
    errors.name = 'Field name must be unique'
  }

  // Label validation
  if (!formData.label.trim()) {
    errors.label = 'Field label is required'
  }

  // Type validation
  if (!formData.type) {
    errors.type = 'Field type is required'
  }

  // Options validation
  if (needsOptions.value) {
    const validOptions = formData.options?.filter((opt) => opt.trim() !== '') || []
    if (validOptions.length === 0) {
      errors.options = 'At least one option is required'
    }
  }

  // Pattern validation
  if (formData.validation_rules?.pattern) {
    try {
      new RegExp(formData.validation_rules.pattern)
    } catch {
      errors.pattern = 'Invalid regular expression'
    }
  }

  return Object.keys(errors).length === 0
}

const handleSave = (): void => {
  if (!validate()) return

  isSaving.value = true

  try {
    // Convert default value string to appropriate type
    let defaultValue: string | number | boolean | string[] | undefined = undefined
    if (defaultValueString.value.trim()) {
      switch (formData.type) {
        case 'number':
          defaultValue = Number(defaultValueString.value)
          break
        case 'checkbox':
          defaultValue = defaultValueString.value === 'true'
          break
        case 'multi_select':
          defaultValue = defaultValueString.value.split(',').map((s) => s.trim())
          break
        default:
          defaultValue = defaultValueString.value
      }
    }

    const field: SchemaField = {
      name: formData.name.trim(),
      label: formData.label.trim(),
      type: formData.type,
      description: formData.description?.trim() || undefined,
      required: formData.required,
      default_value: defaultValue,
      options: needsOptions.value ? formData.options?.filter((opt) => opt.trim() !== '') : undefined,
      validation_rules: Object.keys(formData.validation_rules || {}).length > 0
        ? formData.validation_rules
        : undefined,
      placeholder: formData.placeholder?.trim() || undefined,
      help_text: formData.help_text?.trim() || undefined
    }

    emit('save', field)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped lang="css">
.field-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface, #ffffff);
  border-left: 1px solid var(--color-border, #e5e7eb);
}

.field-editor__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.field-editor__title {
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.field-editor__form {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
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

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.options-list__item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.validation-rules {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.validation-rules__row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-error {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-error, #ef4444);
  margin-top: 4px;
}

.field-editor__actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid var(--color-border, #e5e7eb);
  margin-top: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .field-editor {
    border-left: none;
    border-top: 1px solid var(--color-border, #e5e7eb);
  }

  .validation-rules__row {
    grid-template-columns: 1fr;
  }
}
</style>



