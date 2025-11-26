<template>
  <div class="upload-step">
    <div class="upload-step__header">
      <h2 class="upload-step__title">Upload Your Files</h2>
      <p class="upload-step__description">
        Drag and drop files here or click to browse. You can upload multiple files at once.
      </p>
    </div>

    <!-- Upload Zone -->
    <div
      class="upload-step__drop-zone"
      :class="{ 'upload-step__drop-zone--active': isDragging }"
      role="region"
      aria-label="Drag and drop files here"
      tabindex="0"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
      @keydown.enter.prevent="triggerFileDialog"
      @keydown.space.prevent="triggerFileDialog"
    >
      <div class="upload-step__drop-content">
        <div class="upload-step__icon">
          <svg class="w-16 h-16 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <div class="upload-step__text">
          <p class="upload-step__primary-text">
            Drop your files here, or
            <button
              type="button"
              class="upload-step__browse-btn"
              @click="triggerFileDialog"
            >
              browse
            </button>
          </p>
          <p class="upload-step__secondary-text">
            Support for images, videos, documents, and more
          </p>
        </div>
      </div>

      <input
        ref="fileInput"
        type="file"
        multiple
        :accept="acceptString"
        class="upload-step__file-input"
        aria-hidden="true"
        @change="handleFileSelect"
      />
    </div>

    <!-- File Limits Info -->
    <div class="upload-step__limits">
      <div class="upload-step__limit-item">
        <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Maximum file size: 500MB</span>
      </div>
      <div class="upload-step__limit-item">
        <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Total upload limit: 2GB</span>
      </div>
    </div>

    <!-- File List -->
    <div v-if="files.length > 0" class="upload-step__files">
      <div class="upload-step__files-header">
        <h3 class="upload-step__files-title">
          Files to Upload ({{ files.length }})
        </h3>
        <Button
          variant="outline"
          size="sm"
          @click="clearAllFiles"
          :disabled="isUploading"
        >
          Clear All
        </Button>
      </div>

      <div class="upload-step__files-list">
        <div
          v-for="file in files"
          :key="file.id"
          class="upload-step__file-item"
        >
          <!-- File Preview -->
          <div class="upload-step__file-preview">
            <img
              v-if="file.preview"
              :src="file.preview"
              :alt="`Preview of ${file.name}`"
              class="upload-step__file-thumbnail"
            />
            <div
              v-else
              class="upload-step__file-icon"
              :class="getFileIconClass(file.type)"
            >
              {{ getFileIcon(file.type) }}
            </div>
          </div>

          <!-- File Info -->
          <div class="upload-step__file-info">
            <div class="upload-step__file-name">
              {{ file.name }}
            </div>
            <div class="upload-step__file-size">
              {{ formatFileSize(file.size) }}
            </div>
          </div>

          <!-- File Status -->
          <div class="upload-step__file-status">
            <div
              v-if="file.uploadStatus === 'uploading'"
              class="upload-step__progress"
            >
              <div class="upload-step__progress-bar">
                <div
                  class="upload-step__progress-fill"
                  :style="{ width: `${file.uploadProgress}%` }"
                ></div>
              </div>
              <span class="upload-step__progress-text">
                {{ file.uploadProgress }}%
              </span>
            </div>

            <div
              v-else-if="file.uploadStatus === 'completed'"
              class="upload-step__status upload-step__status--success"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <div
              v-else-if="file.uploadStatus === 'error'"
              class="upload-step__status upload-step__status--error"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>

          <!-- File Actions -->
          <div class="upload-step__file-actions">
            <Button
              variant="ghost"
              size="sm"
              @click="removeFile(file.id)"
              :disabled="isUploading"
              aria-label="Remove file"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </Button>
          </div>
        </div>
      </div>

      <!-- Error Summary -->
      <div v-if="errorFiles.length > 0" class="upload-step__error-summary">
        <Alert variant="error">
          <strong>{{ errorFiles.length }} file(s) failed to upload:</strong>
          <ul class="mt-2 space-y-1">
            <li v-for="file in errorFiles" :key="file.id">
              {{ file.name }}: {{ file.error }}
            </li>
          </ul>
        </Alert>
      </div>
    </div>

    <!-- Upload Controls -->
    <div v-if="files.length > 0" class="upload-step__controls">
      <div class="upload-step__summary">
        <span class="upload-step__summary-text">
          {{ completedFiles.length }} of {{ files.length }} files ready
        </span>
        <div v-if="isUploading" class="upload-step__overall-progress">
          <div class="upload-step__progress-bar">
            <div
              class="upload-step__progress-fill"
              :style="{ width: `${overallProgress}%` }"
            ></div>
          </div>
          <span class="upload-step__progress-text">
            {{ overallProgress }}%
          </span>
        </div>
      </div>

      <div class="upload-step__actions">
        <Button
          variant="outline"
          @click="$emit('complete')"
          :disabled="!canProceed"
        >
          Continue with {{ completedFiles.length }} file(s)
        </Button>
      </div>
    </div>

    <!-- Screen Reader Status -->
    <div class="sr-only" role="status" aria-live="polite">
      {{ screenReaderStatus }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Upload Step Component
 *
 * Handles file selection, drag & drop, and upload progress.
 * Part of the multi-step upload workflow.
 */

import { ref, computed, watch } from 'vue'
import Button from '@/components/Common/Button.vue'
import Alert from '@/components/Common/Alert.vue'
import { useUploadWorkflowStore, type WorkflowFile } from '@/stores/uploadWorkflowStore'

// Props
const props = defineProps<{
  files: WorkflowFile[]
}>()

// Emits
const emit = defineEmits<{
  'update:files': [files: WorkflowFile[]]
  complete: []
  error: [error: string]
}>()

// Composables
const workflowStore = useUploadWorkflowStore()

// Reactive state
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement>()
const isUploading = ref(false)

// Computed properties
const completedFiles = computed(() =>
  props.files.filter(f => f.uploadStatus === 'completed')
)

const errorFiles = computed(() =>
  props.files.filter(f => f.uploadStatus === 'error')
)

const overallProgress = computed(() => {
  if (props.files.length === 0) return 0
  const totalProgress = props.files.reduce((sum, file) => sum + file.uploadProgress, 0)
  return Math.round(totalProgress / props.files.length)
})

const canProceed = computed(() =>
  completedFiles.value.length > 0 && !isUploading.value
)

const acceptString = computed(() => {
  // Accept all file types for DAM system
  return '*/*'
})

const screenReaderStatus = computed(() => {
  const total = props.files.length
  const completed = completedFiles.value.length
  const errors = errorFiles.value.length

  if (total === 0) return 'No files selected'

  let status = `${completed} of ${total} files uploaded successfully`
  if (errors > 0) {
    status += `, ${errors} files failed`
  }
  if (isUploading.value) {
    status += ', upload in progress'
  }

  return status
})

// Methods
function triggerFileDialog() {
  fileInput.value?.click()
}

function handleDrop(event: DragEvent) {
  isDragging.value = false

  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    addFiles(files)
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files

  if (files && files.length > 0) {
    addFiles(files)
  }

  // Reset input value to allow selecting the same file again
  target.value = ''
}

async function addFiles(files: FileList | File[]) {
  try {
    await workflowStore.addFiles(files)
    emit('update:files', workflowStore.uploadedFiles)
  } catch (error: any) {
    emit('error', error.message || 'Failed to add files')
  }
}

function removeFile(fileId: string) {
  workflowStore.removeFile(fileId)
  emit('update:files', workflowStore.uploadedFiles)
}

function clearAllFiles() {
  workflowStore.resetWorkflow()
  emit('update:files', [])
}

async function startUpload() {
  if (isUploading.value || props.files.length === 0) return

  isUploading.value = true

  try {
    await workflowStore.uploadFiles()
    emit('update:files', workflowStore.uploadedFiles)

    // Auto-proceed if all files uploaded successfully
    if (completedFiles.value.length === props.files.length) {
      emit('complete')
    }
  } catch (error: any) {
    emit('error', error.message || 'Upload failed')
  } finally {
    isUploading.value = false
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

function getFileIconClass(fileType: string): string {
  return 'upload-step__file-icon--generic'
}

// Auto-start upload when files are added
watch(
  () => props.files.length,
  (newLength, oldLength) => {
    if (newLength > oldLength && newLength > 0) {
      // Start upload automatically when files are added
      startUpload()
    }
  }
)

// Prevent default drag behaviors
function preventDefaults(event: Event) {
  event.preventDefault()
  event.stopPropagation()
}

// Add global drag listeners
document.addEventListener('dragenter', preventDefaults, false)
document.addEventListener('dragover', preventDefaults, false)
document.addEventListener('dragleave', preventDefaults, false)
document.addEventListener('drop', preventDefaults, false)
</script>

<style scoped>
.upload-step {
  @apply space-y-6;
}

.upload-step__header {
  @apply text-center mb-8;
}

.upload-step__title {
  @apply text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2;
}

.upload-step__description {
  @apply text-neutral-600 dark:text-neutral-400;
}

.upload-step__drop-zone {
  @apply relative border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg p-8 transition-colors cursor-pointer;
  @apply hover:border-primary-400 dark:hover:border-primary-500 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-500/20;
}

.upload-step__drop-zone--active {
  @apply border-primary-500 bg-primary-50 dark:bg-primary-900/20;
}

.upload-step__drop-content {
  @apply flex flex-col items-center space-y-4;
}

.upload-step__icon {
  @apply text-neutral-400 dark:text-neutral-500;
}

.upload-step__text {
  @apply text-center;
}

.upload-step__primary-text {
  @apply text-lg font-medium text-neutral-700 dark:text-neutral-300;
}

.upload-step__browse-btn {
  @apply text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 underline;
}

.upload-step__secondary-text {
  @apply text-sm text-neutral-500 dark:text-neutral-400 mt-1;
}

.upload-step__file-input {
  @apply absolute inset-0 w-full h-full opacity-0 cursor-pointer;
}

.upload-step__limits {
  @apply flex flex-wrap gap-4 text-sm text-neutral-500 dark:text-neutral-400 justify-center;
}

.upload-step__limit-item {
  @apply flex items-center space-x-2;
}

.upload-step__files {
  @apply space-y-4;
}

.upload-step__files-header {
  @apply flex items-center justify-between;
}

.upload-step__files-title {
  @apply text-lg font-medium text-neutral-900 dark:text-neutral-100;
}

.upload-step__files-list {
  @apply space-y-3;
}

.upload-step__file-item {
  @apply flex items-center space-x-4 p-4 bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700;
}

.upload-step__file-preview {
  @apply flex-shrink-0;
}

.upload-step__file-thumbnail {
  @apply w-12 h-12 object-cover rounded;
}

.upload-step__file-icon {
  @apply w-12 h-12 bg-neutral-100 dark:bg-neutral-700 rounded flex items-center justify-center text-xl;
}

.upload-step__file-info {
  @apply flex-1 min-w-0;
}

.upload-step__file-name {
  @apply text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate;
}

.upload-step__file-size {
  @apply text-xs text-neutral-500 dark:text-neutral-400;
}

.upload-step__file-status {
  @apply flex-shrink-0;
}

.upload-step__progress {
  @apply flex items-center space-x-2;
}

.upload-step__progress-bar {
  @apply w-20 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden;
}

.upload-step__progress-fill {
  @apply h-full bg-primary-600 transition-all duration-300;
}

.upload-step__progress-text {
  @apply text-xs text-neutral-600 dark:text-neutral-400;
}

.upload-step__status {
  @apply w-6 h-6 rounded-full flex items-center justify-center;
}

.upload-step__status--success {
  @apply bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400;
}

.upload-step__status--error {
  @apply bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400;
}

.upload-step__file-actions {
  @apply flex-shrink-0;
}

.upload-step__error-summary {
  @apply mt-4;
}

.upload-step__controls {
  @apply flex items-center justify-between pt-6 border-t border-neutral-200 dark:border-neutral-700;
}

.upload-step__summary {
  @apply flex items-center space-x-4;
}

.upload-step__summary-text {
  @apply text-sm font-medium text-neutral-700 dark:text-neutral-300;
}

.upload-step__overall-progress {
  @apply flex items-center space-x-2;
}

.upload-step__actions {
  @apply flex space-x-3;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .upload-step__file-item {
    @apply flex-col space-x-0 space-y-3 p-3;
  }

  .upload-step__file-info {
    @apply text-center;
  }

  .upload-step__controls {
    @apply flex-col space-y-4;
  }

  .upload-step__summary {
    @apply flex-col space-x-0 space-y-2 items-center;
  }
}
</style>
