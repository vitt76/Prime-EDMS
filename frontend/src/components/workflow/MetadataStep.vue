<template>
  <div class="metadata-step">
    <div class="metadata-step__header">
      <h2 class="metadata-step__title">Add Metadata</h2>
      <p class="metadata-step__description">
        Add information about your files to make them easier to find and organize.
      </p>
    </div>

    <!-- Bulk Actions -->
    <div class="metadata-step__bulk-actions">
      <div class="metadata-step__bulk-controls">
        <label class="metadata-step__checkbox">
          <input
            type="checkbox"
            :checked="selectedFiles.length === files.length && files.length > 0"
            :indeterminate="selectedFiles.length > 0 && selectedFiles.length < files.length"
            @change="toggleSelectAll"
          />
          <span class="metadata-step__checkbox-label">
            Select All Files ({{ files.length }})
          </span>
        </label>
      </div>

      <div v-if="selectedFiles.length > 0" class="metadata-step__bulk-fields">
        <p class="metadata-step__bulk-info">
          Apply metadata to {{ selectedFiles.length }} selected file(s):
        </p>

        <div class="metadata-step__bulk-form">
          <div
            v-for="field in bulkFields"
            :key="field.name"
            class="metadata-step__bulk-field"
          >
            <label :for="`bulk-${field.name}`" class="metadata-step__field-label">
              {{ field.label }}
            </label>
            <input
              :id="`bulk-${field.name}`"
              type="text"
              class="metadata-step__field-input"
              :placeholder="field.placeholder"
              v-model="bulkMetadata[field.name]"
              @input="applyBulkMetadata"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- File List with Metadata Forms -->
    <div class="metadata-step__files">
      <div
        v-for="file in files"
        :key="file.id"
        class="metadata-step__file-item"
      >
        <!-- File Header -->
        <div class="metadata-step__file-header">
          <div class="metadata-step__file-select">
            <label class="metadata-step__checkbox">
              <input
                type="checkbox"
                :checked="selectedFiles.includes(file.id)"
                @change="toggleFileSelection(file.id)"
              />
            </label>
          </div>

          <div class="metadata-step__file-info">
            <div class="metadata-step__file-preview">
              <img
                v-if="file.preview"
                :src="file.preview"
                :alt="`Preview of ${file.name}`"
                class="metadata-step__file-thumbnail"
              />
              <div
                v-else
                class="metadata-step__file-icon"
              >
                {{ getFileIcon(file.type) }}
              </div>
            </div>

            <div class="metadata-step__file-details">
              <div class="metadata-step__file-name">
                {{ file.name }}
              </div>
              <div class="metadata-step__file-size">
                {{ formatFileSize(file.size) }}
              </div>
            </div>
          </div>

          <div class="metadata-step__file-status">
            <span
              v-if="hasMetadata(file.id)"
              class="metadata-step__status metadata-step__status--complete"
            >
              Metadata Added
            </span>
            <span
              v-else
              class="metadata-step__status metadata-step__status--pending"
            >
              Add Metadata
            </span>
          </div>
        </div>

        <!-- Metadata Form -->
        <div
          v-if="selectedFiles.includes(file.id)"
          class="metadata-step__form"
        >
          <div class="metadata-step__form-grid">
            <div
              v-for="field in metadataFields"
              :key="field.name"
              class="metadata-step__field"
            >
              <label :for="`${file.id}-${field.name}`" class="metadata-step__field-label">
                {{ field.label }}
                <span v-if="field.required" class="metadata-step__required">*</span>
              </label>

              <!-- Text Input -->
              <input
                v-if="field.type === 'text'"
                :id="`${file.id}-${field.name}`"
                type="text"
                class="metadata-step__field-input"
                :placeholder="field.placeholder"
                :required="field.required"
                v-model="fileMetadata[file.id][field.name]"
                @blur="validateField(file.id, field)"
              />

              <!-- Textarea -->
              <textarea
                v-else-if="field.type === 'textarea'"
                :id="`${file.id}-${field.name}`"
                class="metadata-step__field-textarea"
                :placeholder="field.placeholder"
                :required="field.required"
                v-model="fileMetadata[file.id][field.name]"
                @blur="validateField(file.id, field)"
                rows="3"
              ></textarea>

              <!-- Select -->
              <select
                v-else-if="field.type === 'select'"
                :id="`${file.id}-${field.name}`"
                class="metadata-step__field-select"
                :required="field.required"
                v-model="fileMetadata[file.id][field.name]"
                @change="validateField(file.id, field)"
              >
                <option value="">Select {{ field.label.toLowerCase() }}</option>
                <option
                  v-for="option in field.options"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>

              <!-- Date Input -->
              <input
                v-else-if="field.type === 'date'"
                :id="`${file.id}-${field.name}`"
                type="date"
                class="metadata-step__field-input"
                :required="field.required"
                v-model="fileMetadata[file.id][field.name]"
                @blur="validateField(file.id, field)"
              />

              <!-- Number Input -->
              <input
                v-else-if="field.type === 'number'"
                :id="`${file.id}-${field.name}`"
                type="number"
                class="metadata-step__field-input"
                :placeholder="field.placeholder"
                :required="field.required"
                :min="field.min"
                :max="field.max"
                v-model.number="fileMetadata[file.id][field.name]"
                @blur="validateField(file.id, field)"
              />

              <!-- Checkbox -->
              <label
                v-else-if="field.type === 'boolean'"
                class="metadata-step__checkbox"
              >
                <input
                  :id="`${file.id}-${field.name}`"
                  type="checkbox"
                  v-model="fileMetadata[file.id][field.name]"
                />
                <span class="metadata-step__checkbox-label">{{ field.description || field.label }}</span>
              </label>

              <!-- Tags Input -->
              <div
                v-else-if="field.type === 'tags'"
                class="metadata-step__tags-input"
              >
                <input
                  :id="`${file.id}-${field.name}`"
                  type="text"
                  class="metadata-step__field-input"
                  :placeholder="field.placeholder"
                  @keydown="handleTagInput($event, file.id, field.name)"
                />
                <div class="metadata-step__tags">
                  <span
                    v-for="tag in fileMetadata[file.id][field.name] || []"
                    :key="tag"
                    class="metadata-step__tag"
                  >
                    {{ tag }}
                    <button
                      type="button"
                      class="metadata-step__tag-remove"
                      @click="removeTag(file.id, field.name, tag)"
                      :aria-label="`Remove ${tag} tag`"
                    >
                      ×
                    </button>
                  </span>
                </div>
              </div>

              <!-- Help Text -->
              <div v-if="field.help_text" class="metadata-step__field-help">
                {{ field.help_text }}
              </div>

              <!-- Validation Error -->
              <div
                v-if="fieldErrors[file.id]?.[field.name]"
                class="metadata-step__field-error"
              >
                {{ fieldErrors[file.id][field.name] }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step Controls -->
    <div class="metadata-step__controls">
      <Button
        variant="outline"
        @click="$emit('back')"
      >
        Back
      </Button>

      <Button
        variant="primary"
        @click="handleContinue"
        :disabled="!canContinue"
      >
        Continue to Collections
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Metadata Step Component
 *
 * Allows users to add metadata to uploaded files.
 * Supports bulk operations and dynamic form fields.
 */

import { ref, computed, watch, onMounted } from 'vue'
import Button from '@/components/Common/Button.vue'
import { useUploadWorkflowStore, type WorkflowFile } from '@/stores/uploadWorkflowStore'
import { metadataService } from '@/services/metadataService'

// Types
interface MetadataField {
  name: string
  label: string
  type: 'text' | 'textarea' | 'select' | 'date' | 'number' | 'boolean' | 'tags'
  required: boolean
  placeholder?: string
  help_text?: string
  description?: string
  options?: Array<{ value: string; label: string }>
  min?: number
  max?: number
}

interface FileMetadata {
  [fileId: string]: Record<string, any>
}

// Props
const props = defineProps<{
  files: WorkflowFile[]
  metadata: FileMetadata
}>()

// Emits
const emit = defineEmits<{
  'update:metadata': [metadata: FileMetadata]
  complete: []
  back: []
  error: [error: string]
}>()

// Composables
const workflowStore = useUploadWorkflowStore()

// Reactive state
const metadataSchema = ref<any>(null)
const selectedFiles = ref<string[]>([])
const fileMetadata = ref<FileMetadata>({})
const bulkMetadata = ref<Record<string, any>>({})
const fieldErrors = ref<Record<string, Record<string, string>>>({})

// Computed properties
const metadataFields = computed((): MetadataField[] => {
  if (!metadataSchema.value?.fields) return []

  return metadataSchema.value.fields.map((field: any) => ({
    name: field.name,
    label: field.label,
    type: field.field_type || 'text',
    required: field.required || false,
    placeholder: field.placeholder,
    help_text: field.help_text,
    description: field.description,
    options: field.options,
    min: field.min_value,
    max: field.max_value
  }))
})

const bulkFields = computed(() => {
  return metadataFields.value.filter(field => field.type === 'text' || field.type === 'textarea')
})

const canContinue = computed(() => {
  // At least one file must have metadata
  return Object.keys(fileMetadata.value).some(fileId => {
    const metadata = fileMetadata.value[fileId]
    return metadata && Object.keys(metadata).length > 0
  })
})

// Methods
async function loadMetadataSchema() {
  try {
    // Load default metadata schema for assets
    const schema = await metadataService.getAssetMetadataSchema()
    metadataSchema.value = schema
  } catch (error: any) {
    emit('error', error.message || 'Failed to load metadata schema')
  }
}

function toggleSelectAll() {
  if (selectedFiles.value.length === props.files.length) {
    selectedFiles.value = []
  } else {
    selectedFiles.value = props.files.map(f => f.id)
  }
}

function toggleFileSelection(fileId: string) {
  const index = selectedFiles.value.indexOf(fileId)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
  } else {
    selectedFiles.value.push(fileId)
  }
}

function applyBulkMetadata() {
  selectedFiles.value.forEach(fileId => {
    if (!fileMetadata.value[fileId]) {
      fileMetadata.value[fileId] = {}
    }

    Object.entries(bulkMetadata.value).forEach(([fieldName, value]) => {
      if (value && !fileMetadata.value[fileId][fieldName]) {
        fileMetadata.value[fileId][fieldName] = value
      }
    })
  })

  updateMetadata()
}

function hasMetadata(fileId: string): boolean {
  return fileMetadata.value[fileId] && Object.keys(fileMetadata.value[fileId]).length > 0
}

function validateField(fileId: string, field: MetadataField) {
  if (!fieldErrors.value[fileId]) {
    fieldErrors.value[fileId] = {}
  }

  const value = fileMetadata.value[fileId]?.[field.name]
  let error = ''

  if (field.required && (!value || value.toString().trim() === '')) {
    error = `${field.label} is required`
  }

  if (field.type === 'number') {
    const numValue = Number(value)
    if (field.min !== undefined && numValue < field.min) {
      error = `Must be at least ${field.min}`
    }
    if (field.max !== undefined && numValue > field.max) {
      error = `Must be at most ${field.max}`
    }
  }

  if (field.type === 'date' && value) {
    const date = new Date(value)
    if (isNaN(date.getTime())) {
      error = 'Invalid date format'
    }
  }

  fieldErrors.value[fileId][field.name] = error
}

function handleTagInput(event: KeyboardEvent, fileId: string, fieldName: string) {
  const input = event.target as HTMLInputElement
  const value = input.value.trim()

  if (event.key === 'Enter' && value) {
    event.preventDefault()

    if (!fileMetadata.value[fileId][fieldName]) {
      fileMetadata.value[fileId][fieldName] = []
    }

    if (!fileMetadata.value[fileId][fieldName].includes(value)) {
      fileMetadata.value[fileId][fieldName].push(value)
    }

    input.value = ''
    updateMetadata()
  } else if (event.key === ',' && value) {
    event.preventDefault()

    if (!fileMetadata.value[fileId][fieldName]) {
      fileMetadata.value[fileId][fieldName] = []
    }

    const tagValue = value.replace(/,$/, '')
    if (!fileMetadata.value[fileId][fieldName].includes(tagValue)) {
      fileMetadata.value[fileId][fieldName].push(tagValue)
    }

    input.value = ''
    updateMetadata()
  }
}

function removeTag(fileId: string, fieldName: string, tagToRemove: string) {
  const tags = fileMetadata.value[fileId][fieldName] || []
  fileMetadata.value[fileId][fieldName] = tags.filter((tag: string) => tag !== tagToRemove)
  updateMetadata()
}

function updateMetadata() {
  emit('update:metadata', { ...fileMetadata.value })
}

function handleContinue() {
  if (canContinue.value) {
    // Validate all fields before proceeding
    let hasErrors = false
    props.files.forEach(file => {
      if (selectedFiles.value.includes(file.id)) {
        metadataFields.value.forEach(field => {
          validateField(file.id, field)
          if (fieldErrors.value[file.id]?.[field.name]) {
            hasErrors = true
          }
        })
      }
    })

    if (!hasErrors) {
      emit('complete')
    }
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function getFileIcon(fileType: string): string {
  if (fileType.startsWith('image/')) return '🖼️'
  if (fileType.startsWith('video/')) return '🎥'
  if (fileType.startsWith('audio/')) return '🎵'
  if (fileType.includes('pdf')) return '📄'
  if (fileType.includes('document') || fileType.includes('word')) return '📝'
  if (fileType.includes('spreadsheet') || fileType.includes('excel')) return '📊'
  if (fileType.includes('presentation') || fileType.includes('powerpoint')) return '📽️'
  if (fileType.includes('zip') || fileType.includes('archive')) return '📦'

  return '📄'
}

// Initialize metadata for all files
function initializeMetadata() {
  props.files.forEach(file => {
    if (!fileMetadata.value[file.id]) {
      fileMetadata.value[file.id] = {}
    }
  })
}

// Watch for prop changes
watch(
  () => props.metadata,
  (newMetadata) => {
    fileMetadata.value = { ...newMetadata }
  },
  { immediate: true }
)

watch(
  () => props.files,
  () => {
    initializeMetadata()
  },
  { immediate: true }
)

// Load metadata schema on mount
onMounted(() => {
  loadMetadataSchema()
  initializeMetadata()
})
</script>

<style scoped>
.metadata-step {
  @apply space-y-6;
}

.metadata-step__header {
  @apply text-center mb-8;
}

.metadata-step__title {
  @apply text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2;
}

.metadata-step__description {
  @apply text-neutral-600 dark:text-neutral-400;
}

.metadata-step__bulk-actions {
  @apply bg-neutral-50 dark:bg-neutral-800 rounded-lg p-6 space-y-4;
}

.metadata-step__bulk-controls {
  @apply flex items-center;
}

.metadata-step__checkbox {
  @apply flex items-center space-x-2 cursor-pointer;
}

.metadata-step__checkbox input[type="checkbox"] {
  @apply w-4 h-4 text-primary-600 bg-neutral-100 border-neutral-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-neutral-800 focus:ring-2 dark:bg-neutral-700 dark:border-neutral-600;
}

.metadata-step__checkbox-label {
  @apply text-sm font-medium text-neutral-700 dark:text-neutral-300;
}

.metadata-step__bulk-fields {
  @apply space-y-3;
}

.metadata-step__bulk-info {
  @apply text-sm text-neutral-600 dark:text-neutral-400;
}

.metadata-step__bulk-form {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.metadata-step__bulk-field {
  @apply space-y-2;
}

.metadata-step__files {
  @apply space-y-6;
}

.metadata-step__file-item {
  @apply bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden;
}

.metadata-step__file-header {
  @apply flex items-center space-x-4 p-4;
}

.metadata-step__file-select {
  @apply flex-shrink-0;
}

.metadata-step__file-info {
  @apply flex items-center space-x-3 flex-1;
}

.metadata-step__file-preview {
  @apply flex-shrink-0;
}

.metadata-step__file-thumbnail {
  @apply w-12 h-12 object-cover rounded;
}

.metadata-step__file-icon {
  @apply w-12 h-12 bg-neutral-100 dark:bg-neutral-700 rounded flex items-center justify-center text-xl;
}

.metadata-step__file-details {
  @apply flex-1 min-w-0;
}

.metadata-step__file-name {
  @apply text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate;
}

.metadata-step__file-size {
  @apply text-xs text-neutral-500 dark:text-neutral-400;
}

.metadata-step__file-status {
  @apply flex-shrink-0;
}

.metadata-step__status {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
}

.metadata-step__status--complete {
  @apply bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400;
}

.metadata-step__status--pending {
  @apply bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-400;
}

.metadata-step__form {
  @apply border-t border-neutral-200 dark:border-neutral-700 p-4;
}

.metadata-step__form-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.metadata-step__field {
  @apply space-y-2;
}

.metadata-step__field-label {
  @apply block text-sm font-medium text-neutral-700 dark:text-neutral-300;
}

.metadata-step__required {
  @apply text-red-500 ml-1;
}

.metadata-step__field-input,
.metadata-step__field-textarea,
.metadata-step__field-select {
  @apply block w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm placeholder-neutral-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:placeholder-neutral-300 dark:focus:ring-primary-600 dark:focus:border-primary-600 sm:text-sm;
}

.metadata-step__field-textarea {
  @apply resize-none;
}

.metadata-step__tags-input {
  @apply space-y-2;
}

.metadata-step__tags {
  @apply flex flex-wrap gap-2;
}

.metadata-step__tag {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900/20 dark:text-primary-400;
}

.metadata-step__tag-remove {
  @apply ml-1 text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300 focus:outline-none;
}

.metadata-step__field-help {
  @apply text-xs text-neutral-500 dark:text-neutral-400;
}

.metadata-step__field-error {
  @apply text-xs text-red-600 dark:text-red-400;
}

.metadata-step__controls {
  @apply flex justify-between pt-6 border-t border-neutral-200 dark:border-neutral-700;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .metadata-step__file-header {
    @apply flex-col space-x-0 space-y-3 items-start;
  }

  .metadata-step__form-grid {
    @apply grid-cols-1;
  }

  .metadata-step__controls {
    @apply flex-col space-y-4;
  }
}
</style>











