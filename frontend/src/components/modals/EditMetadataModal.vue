<template>
  <Modal
    :isOpen="isOpen"
    title="Edit metadata"
    size="lg"
    @close="handleCancel"
  >
    <div class="edit-metadata-modal">
      <div v-if="isLoadingSchema" class="edit-metadata-modal__empty">
        Loading metadata schema…
      </div>
      <div v-else-if="schemaError" class="edit-metadata-modal__error" role="alert">
        {{ schemaError }}
      </div>
      <div v-else-if="!metadataSchema || !metadataSchema.fields.length" class="edit-metadata-modal__empty">
        No metadata fields are configured for this schema.
      </div>
      <form
        v-else
        class="edit-metadata-modal__form"
        @submit.prevent="handleSave"
        novalidate
      >
        <p class="edit-metadata-modal__intro">
          {{ introText }}
        </p>

        <div
          v-for="field in metadataSchema.fields"
          :key="field.name"
          class="edit-metadata-modal__field"
        >
          <div class="edit-metadata-modal__field-header">
            <label :for="`field-${field.name}`" class="edit-metadata-modal__label">
              {{ field.label }}
              <span v-if="field.required" class="edit-metadata-modal__required-indicator">*</span>
            </label>
            <span v-if="field.helper_text" class="edit-metadata-modal__help-text">
              {{ field.helper_text }}
            </span>
          </div>

          <div class="edit-metadata-modal__input-wrapper">
            <input
              v-if="field.field_type === 'text' || field.field_type === 'url' || field.field_type === 'email'"
              :id="`field-${field.name}`"
              type="text"
              class="edit-metadata-modal__input"
              :placeholder="field.placeholder"
              v-model="formState[field.name]"
              @blur="validateField(field.name)"
            />

            <textarea
              v-else-if="field.field_type === 'textarea'"
              :id="`field-${field.name}`"
              class="edit-metadata-modal__textarea"
              :placeholder="field.placeholder"
              :value="String(formState[field.name] ?? '')"
              @input="formState[field.name] = ($event.target as HTMLTextAreaElement).value"
              rows="3"
              @blur="validateField(field.name)"
            />

            <input
              v-else-if="field.field_type === 'number'"
              :id="`field-${field.name}`"
              type="number"
              class="edit-metadata-modal__input"
              :placeholder="field.placeholder"
              v-model="formState[field.name]"
              @blur="validateField(field.name)"
            />

            <input
              v-else-if="field.field_type === 'date'"
              :id="`field-${field.name}`"
              type="date"
              class="edit-metadata-modal__input"
              v-model="formState[field.name]"
              @blur="validateField(field.name)"
            />

            <input
              v-else-if="field.field_type === 'datetime'"
              :id="`field-${field.name}`"
              type="datetime-local"
              class="edit-metadata-modal__input"
              v-model="formState[field.name]"
              @blur="validateField(field.name)"
            />

            <select
              v-else-if="field.field_type === 'select'"
              :id="`field-${field.name}`"
              class="edit-metadata-modal__input"
              v-model="formState[field.name]"
              @blur="validateField(field.name)"
            >
              <option value="">Select...</option>
              <option
                v-for="option in field.options || []"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>

            <select
              v-else-if="field.field_type === 'multiselect'"
              :id="`field-${field.name}`"
              class="edit-metadata-modal__input"
              multiple
              @change="handleMultiSelectChange(field.name, $event)"
              :value="formState[field.name]"
            >
              <option
                v-for="option in field.options || []"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>

            <label
              v-else-if="field.field_type === 'boolean'"
              class="edit-metadata-modal__checkbox"
            >
              <input
                type="checkbox"
                :id="`field-${field.name}`"
                v-model="formState[field.name]"
                @change="validateField(field.name)"
              />
              <span>{{ field.label || 'Toggle option' }}</span>
            </label>

            <p
              v-else
              class="edit-metadata-modal__unsupported"
            >
              Unsupported field type: {{ field.field_type }}
            </p>
          </div>

          <p
            v-if="validationErrors[field.name]"
            class="edit-metadata-modal__error-message"
          >
            {{ validationErrors[field.name] }}
          </p>

          <div v-if="isBulkEdit" class="edit-metadata-modal__bulk-checkbox">
            <label>
              <input
                type="checkbox"
                v-model="fieldApplyAll[field.name]"
                :disabled="!isFieldDirty(field.name)"
              />
              Apply changes for this field to all selected assets
            </label>
          </div>
        </div>
      </form>
    </div>

    <template #footer>
      <Button variant="ghost" class="w-32" @click="handleCancel">
        Cancel
      </Button>
      <Button
        variant="primary"
        class="w-32"
        :loading="isSaving"
        :disabled="!formIsDirty || !formIsValid || isSaving"
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
import { metadataService } from '@/services/metadataService'
import { useAdminStore } from '@/stores/adminStore'
import { useUIStore } from '@/stores/uiStore'
import { formatApiError } from '@/utils/errors'
import type { Asset } from '@/types/api'
import type { MetadataSchema, MetadataType, MetadataFieldType } from '@/types/admin'

// Alias for backward compatibility
type SchemaField = MetadataType

interface Props {
  isOpen: boolean
  schemaId?: number
  schema?: MetadataSchema | null
  asset?: Asset
  assets?: Asset[]
}

const props = withDefaults(defineProps<Props>(), {
  assets: () => [],
  schema: null
})

const emit = defineEmits<{
  close: []
  saved: []
}>()

const adminStore = useAdminStore()
const uiStore = useUIStore()

const metadataSchema = ref<MetadataSchema | null>(props.schema ?? null)
const schemaError = ref<string | null>(null)
const isLoadingSchema = ref(false)
const isSaving = ref(false)
const formState = reactive<Record<string, string | number | boolean | string[] | null>>({})
const initialValues = ref<Record<string, string | number | boolean | string[] | null>>({})
const validationErrors = reactive<Record<string, string | null>>({})
const fieldApplyAll = reactive<Record<string, boolean>>({})
const touchedFields = reactive<Record<string, boolean>>({})

const selectedAssets = computed<Asset[]>(() => {
  if (props.assets && props.assets.length > 0) {
    return props.assets
  }
  if (props.asset) {
    return [props.asset]
  }
  return []
})

const isBulkEdit = computed(() => selectedAssets.value.length > 1)
const introText = computed(() => {
  if (!metadataSchema.value) return 'No schema selected.'
  if (isBulkEdit.value) {
    return `Updating metadata for ${selectedAssets.value.length} assets.`
  }
  return 'Editing metadata for a single asset.'
})

const formIsValid = computed(() => {
  if (!metadataSchema.value) return false
  return metadataSchema.value.fields.every(
    (field) => !validationErrors[field.name]
  )
})

const formIsDirty = computed(() => {
  if (!metadataSchema.value) return false
  return metadataSchema.value.fields.some((field) => isFieldDirty(field.name))
})

async function loadSchema(): Promise<void> {
  schemaError.value = null
  if (props.schema) {
    metadataSchema.value = props.schema
    return
  }

  if (!props.schemaId) {
    metadataSchema.value = null
    schemaError.value = 'Metadata schema is missing.'
    return
  }

  isLoadingSchema.value = true
  try {
    const schema = await adminStore.getSchema(props.schemaId)
    metadataSchema.value = schema
  } catch (error) {
    metadataSchema.value = null
    schemaError.value = formatApiError(error)
  } finally {
    isLoadingSchema.value = false
  }
}

function initializeForm(): void {
  resetFormState()
  const schema = metadataSchema.value
  if (!schema) return

  const referenceMetadata = selectedAssets.value[0]?.metadata ?? {}
  schema.fields.forEach((field) => {
    const rawValue =
      referenceMetadata?.[field.name] ??
      field.default ??
      getDefaultValueForField(field)
    formState[field.name] = normalizeForForm(field, rawValue)
    initialValues.value[field.name] = normalizeForForm(field, rawValue)
    validationErrors[field.name] = null
    fieldApplyAll[field.name] = true
    touchedFields[field.name] = false
  })
}

function resetFormState(): void {
  Object.keys(formState).forEach((key) => delete formState[key])
  initialValues.value = {}
  Object.keys(validationErrors).forEach((key) => {
    delete validationErrors[key]
  })
  Object.keys(fieldApplyAll).forEach((key) => delete fieldApplyAll[key])
  Object.keys(touchedFields).forEach((key) => delete touchedFields[key])
}

function handleCancel(): void {
  resetFormState()
  emit('close')
}

function isFieldDirty(name: string): boolean {
  const schema = metadataSchema.value
  if (!schema) return false
  const field = schema.fields.find((item) => item.name === name)
  if (!field) return false
  const current = formState[name]
  const initial = initialValues.value[name]
  return getComparableValue(field, current) !== getComparableValue(field, initial)
}

function setFieldValue(name: string, value: FormValue): void {
  formState[name] = value
  touchedFields[name] = true
  validationErrors[name] = validateField(name)
}

function handleMultiSelectChange(name: string, event: Event): void {
  const target = event.target as HTMLSelectElement
  const values = Array.from(target.selectedOptions).map((option) => option.value)
  setFieldValue(name, values)
}

function validateField(name: string): string | null {
  const schema = metadataSchema.value
  if (!schema) return null
  const field = schema.fields.find((item) => item.name === name)
  if (!field) return null
  const value = formState[name]
  
  // Check required
  if (field.required && isEmpty(value, field.field_type)) {
    return 'This field is required.'
  }
  
  // Validate using field.validation (regex or Python path)
  if (field.validation && typeof value === 'string' && value !== '') {
    try {
      // Try to use as regex pattern
      const pattern = new RegExp(field.validation)
      if (!pattern.test(value)) {
        return 'Value does not match the required pattern.'
      }
    } catch {
      // Not a valid regex, skip validation
    }
  }
  
  return null
}

async function handleSave(): Promise<void> {
  if (!metadataSchema.value) return
  if (!formIsDirty.value) {
    uiStore.addNotification({
      type: 'info',
      message: 'No metadata changes detected.'
    })
    return
  }
  if (!formIsValid.value) {
    uiStore.addNotification({
      type: 'error',
      message: 'Fix validation errors before saving.'
    })
    return
  }

  isSaving.value = true
  try {
    const changedFieldNames = metadataSchema.value.fields
      .filter((field) => shouldIncludeField(field.name) && isFieldDirty(field.name))
      .map((field) => field.name)

    if (!changedFieldNames.length) {
      uiStore.addNotification({
        type: 'info',
        message: 'No metadata fields to update.'
      })
      return
    }

    for (const asset of selectedAssets.value) {
      const documentId = asset.id
      
      // Use Mayan EDMS metadata API
      for (const fieldName of changedFieldNames) {
        const field = metadataSchema.value.fields.find((item) => item.name === fieldName)
        if (!field) continue
        if (!shouldIncludeField(field.name)) continue
        
        const value = String(normalizeForPayload(field, formState[field.name]) || '')
        
        try {
          // Try to update using metadataService
          await metadataService.updateAssetMetadata(String(documentId), {
            [field.name]: value
          })
        } catch (updateError) {
          console.warn(`[EditMetadataModal] Failed to update ${field.name}:`, updateError)
          // Continue with other fields
        }
      }
    }

    uiStore.addNotification({
      type: 'success',
      title: 'Metadata updated',
      message: 'Asset metadata has been saved.'
    })
    emit('saved')
    handleCancel()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: formatApiError(error)
    })
  } finally {
    isSaving.value = false
  }
}

function shouldIncludeField(name: string): boolean {
  if (!isBulkEdit.value) {
    return true
  }
  return fieldApplyAll[name] ?? true
}

type FormValue = string | number | boolean | string[] | null

function normalizeForForm(field: SchemaField, value: unknown): FormValue {
  const fieldType = field.field_type
  if (fieldType === 'boolean') {
    return Boolean(value)
  }
  if (fieldType === 'multiselect') {
    return Array.isArray(value) ? [...value] as string[] : []
  }
  if (fieldType === 'number') {
    return (value as number) ?? ''
  }
  return (value as string) ?? ''
}

function normalizeForPayload(field: SchemaField, value: unknown): unknown {
  const fieldType = field.field_type
  if (fieldType === 'boolean') {
    return Boolean(value)
  }
  if (fieldType === 'number') {
    if (typeof value === 'string' && value !== '') {
      const parsed = Number(value)
      return Number.isNaN(parsed) ? null : parsed
    }
    return null
  }
  if (fieldType === 'multiselect') {
    return Array.isArray(value) ? value : []
  }
  return value
}

function getComparableValue(field: SchemaField, value: unknown): string {
  const fieldType = field.field_type
  if (fieldType === 'multiselect') {
    const list = Array.isArray(value) ? [...value].sort() : []
    return JSON.stringify(list)
  }
  if (fieldType === 'boolean') {
    return value ? '1' : '0'
  }
  if (typeof value === 'number') {
    return value.toString()
  }
  if (Array.isArray(value)) {
    return JSON.stringify(value)
  }
  return String(value ?? '')
}

function getDefaultValueForField(field: SchemaField): string | boolean | string[] {
  const fieldType = field.field_type
  if (fieldType === 'boolean') {
    return Boolean(field.default)
  }
  if (fieldType === 'multiselect') {
    // default is a string in MetadataType
    return []
  }
  return field.default ?? ''
}

function isEmpty(value: unknown, fieldType: MetadataFieldType): boolean {
  if (fieldType === 'boolean') {
    return value !== true
  }
  if (fieldType === 'multiselect') {
    return !Array.isArray(value) || value.length === 0
  }
  if (value === null || value === undefined) {
    return true
  }
  if (typeof value === 'string') {
    return value.trim() === ''
  }
  return false
}

watch(
  () => props.isOpen,
  async (open) => {
    if (open) {
      await loadSchema()
      initializeForm()
    } else {
      resetFormState()
    }
  }
)

watch(
  () => props.schema,
  (schema) => {
    if (schema) {
      metadataSchema.value = schema
      if (props.isOpen) {
        initializeForm()
      }
    }
  }
)

watch(
  () => props.schemaId,
  async (schemaId) => {
    if (props.isOpen && schemaId) {
      await loadSchema()
      initializeForm()
    }
  }
)

watch(
  () => selectedAssets.value,
  () => {
    if (props.isOpen && metadataSchema.value) {
      initializeForm()
    }
  },
  { deep: true }
)
</script>

<style scoped>
:global(.modal__content) {
  max-width: 960px;
}

.edit-metadata-modal {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.edit-metadata-modal__intro {
  margin: 0;
  font-size: 0.95rem;
  color: #475569;
}

.edit-metadata-modal__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.edit-metadata-modal__field {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem;
  background: #fff;
}

.edit-metadata-modal__field-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}

.edit-metadata-modal__label {
  font-weight: 600;
  margin-bottom: 0.25rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.edit-metadata-modal__required-indicator {
  color: #dc2626;
}

.edit-metadata-modal__help-text {
  font-size: 0.8rem;
  color: #64748b;
}

.edit-metadata-modal__input-wrapper {
  margin-top: 0.5rem;
}

.edit-metadata-modal__input,
.edit-metadata-modal__textarea,
.edit-metadata-modal__unsupported {
  width: 100%;
  border: 1px solid #cbd5f5;
  border-radius: 0.5rem;
  padding: 0.55rem 0.75rem;
  font-size: 1rem;
  background: #fff;
  color: #0f172a;
}

.edit-metadata-modal__textarea {
  resize: vertical;
  min-height: 88px;
}

.edit-metadata-modal__checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #1e293b;
}

.edit-metadata-modal__error {
  color: #dc2626;
  font-weight: 500;
}

.edit-metadata-modal__error-message {
  margin: 0.35rem 0 0;
  font-size: 0.85rem;
  color: #dc2626;
}

.edit-metadata-modal__bulk-checkbox {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #475569;
}

.edit-metadata-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e2e8f0;
}

.edit-metadata-modal__empty {
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
}
</style>


