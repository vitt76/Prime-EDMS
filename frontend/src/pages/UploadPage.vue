<template>
  <div class="upload-workflow-page">
    <!-- Header with progress -->
    <header class="upload-workflow-page__header">
      <div class="upload-workflow-page__nav">
        <Button
          variant="ghost"
          size="sm"
          @click="handleBackToGallery"
          class="upload-workflow-page__back-btn"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Gallery
        </Button>
      </div>

      <div class="upload-workflow-page__progress">
        <div class="upload-workflow-page__steps">
          <div
            v-for="(step, index) in steps"
            :key="step.id"
            class="upload-workflow-page__step"
            :class="{
              'upload-workflow-page__step--active': currentStep === index,
              'upload-workflow-page__step--completed': currentStep > index,
              'upload-workflow-page__step--disabled': currentStep < index
            }"
          >
            <div class="upload-workflow-page__step-indicator">
              <span v-if="currentStep > index" class="upload-workflow-page__step-check">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span class="upload-workflow-page__step-label">{{ step.title }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main content area -->
    <main class="upload-workflow-page__content">
      <!-- Upload Step -->
      <div v-if="currentStep === 0" class="upload-workflow-page__step-content">
        <UploadStep
          v-model:files="uploadedFiles"
          @complete="handleUploadComplete"
          @error="handleStepError"
        />
      </div>

      <!-- Metadata Step -->
      <div v-else-if="currentStep === 1" class="upload-workflow-page__step-content">
        <MetadataStep
          :files="uploadedFiles"
          v-model:metadata="filesMetadata"
          @complete="handleMetadataComplete"
          @back="handleStepBack"
          @error="handleStepError"
        />
      </div>

      <!-- Collection Step -->
      <div v-else-if="currentStep === 2" class="upload-workflow-page__step-content">
        <CollectionStep
          v-model:selected-collection="selectedCollection"
          @complete="handleCollectionComplete"
          @back="handleStepBack"
          @error="handleStepError"
        />
      </div>

      <!-- Share Step -->
      <div v-else-if="currentStep === 3" class="upload-workflow-page__step-content">
        <ShareStep
          :files="uploadedFiles"
          :metadata="filesMetadata"
          :collection="selectedCollection"
          @complete="handleWorkflowComplete"
          @back="handleStepBack"
          @error="handleStepError"
        />
      </div>
    </main>

    <!-- Global error state -->
    <Alert
      v-if="globalError"
      variant="error"
      class="upload-workflow-page__global-error"
      :dismissible="true"
      @dismiss="globalError = null"
    >
      {{ globalError }}
    </Alert>

    <!-- Loading overlay -->
    <div v-if="isProcessing" class="upload-workflow-page__loading-overlay">
      <div class="upload-workflow-page__loading-content">
        <Spinner size="lg" />
        <p class="upload-workflow-page__loading-text">{{ processingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Upload Workflow Page
 *
 * Multi-step upload workflow following Dropbox/Google Drive pattern:
 * 1. Upload files (drag & drop)
 * 2. Edit metadata (dynamic forms)
 * 3. Assign to collection (tree select)
 * 4. Share (generate links with permissions)
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Button from '@/components/Common/Button.vue'
import Alert from '@/components/Common/Alert.vue'
import Spinner from '@/components/Common/Spinner.vue'
import UploadStep from '@/components/workflow/UploadStep.vue'
import MetadataStep from '@/components/workflow/MetadataStep.vue'
import CollectionStep from '@/components/workflow/CollectionStep.vue'
import ShareStep from '@/components/workflow/ShareStep.vue'
import { useUploadWorkflowStore } from '@/stores/uploadWorkflowStore'

// Types
interface WorkflowFile {
  id: string
  file: File
  name: string
  size: number
  type: string
  uploadProgress: number
  uploadStatus: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
  preview?: string
}

interface FileMetadata {
  [fileId: string]: Record<string, any>
}

interface Collection {
  id: string
  name: string
  path: string[]
}

// Composables
const router = useRouter()
const workflowStore = useUploadWorkflowStore()

// Reactive state
const currentStep = ref(0)
const uploadedFiles = ref<WorkflowFile[]>([])
const filesMetadata = ref<FileMetadata>({})
const selectedCollection = ref<Collection | null>(null)
const globalError = ref<string | null>(null)
const isProcessing = ref(false)
const processingMessage = ref('')

// Workflow steps definition
const steps = [
  { id: 'upload', title: 'Upload Files' },
  { id: 'metadata', title: 'Add Metadata' },
  { id: 'collection', title: 'Choose Collection' },
  { id: 'share', title: 'Share & Finish' }
]

// Computed properties
const canProceedToNext = computed(() => {
  switch (currentStep.value) {
    case 0: return uploadedFiles.value.length > 0 && uploadedFiles.value.every(f => f.uploadStatus === 'completed')
    case 1: return Object.keys(filesMetadata.value).length > 0
    case 2: return selectedCollection.value !== null
    case 3: return true // Share step is always ready
    default: return false
  }
})

const canGoBack = computed(() => {
  return currentStep.value > 0
})

// Methods
function handleBackToGallery() {
  if (confirm('Are you sure you want to leave? Your progress will be lost.')) {
    router.push('/dam')
  }
}

function handleUploadComplete() {
  if (canProceedToNext.value) {
    proceedToNextStep()
  }
}

function handleMetadataComplete() {
  if (canProceedToNext.value) {
    proceedToNextStep()
  }
}

function handleCollectionComplete() {
  if (canProceedToNext.value) {
    proceedToNextStep()
  }
}

function handleWorkflowComplete() {
  // Workflow completed successfully
  router.push('/dam')
}

function handleStepBack() {
  if (canGoBack.value) {
    currentStep.value--
  }
}

function handleStepError(error: string) {
  globalError.value = error
}

function proceedToNextStep() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

// Global processing state management
function setProcessing(message: string) {
  isProcessing.value = true
  processingMessage.value = message
}

function clearProcessing() {
  isProcessing.value = false
  processingMessage.value = ''
}

// Watch for processing state changes
watch(
  () => workflowStore.isProcessing,
  (newValue) => {
    if (newValue) {
      setProcessing(workflowStore.processingMessage)
    } else {
      clearProcessing()
    }
  }
)

// Watch for global errors
watch(
  () => workflowStore.error,
  (newValue) => {
    if (newValue) {
      globalError.value = newValue
    }
  }
)

// Initialize workflow
onMounted(() => {
  // Reset workflow state
  workflowStore.resetWorkflow()

  // Initialize with any pre-uploaded files from route params if needed
  // const filesFromParams = router.currentRoute.value.query.files
  // if (filesFromParams) {
  //   // Handle pre-uploaded files
  // }
})
</script>

<style scoped>
.upload-workflow-page {
  @apply min-h-screen bg-neutral-50 dark:bg-neutral-900;
}

.upload-workflow-page__header {
  @apply bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 px-6 py-4;
}

.upload-workflow-page__nav {
  @apply mb-4;
}

.upload-workflow-page__back-btn {
  @apply text-neutral-600 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-neutral-200;
}

.upload-workflow-page__progress {
  @apply w-full;
}

.upload-workflow-page__steps {
  @apply flex items-center justify-between max-w-2xl mx-auto;
}

.upload-workflow-page__step {
  @apply flex flex-col items-center flex-1;
}

.upload-workflow-page__step:not(:last-child)::after {
  content: '';
  @apply absolute top-6 left-1/2 w-full h-0.5 bg-neutral-200 dark:bg-neutral-700 -translate-y-1/2;
}

.upload-workflow-page__step-indicator {
  @apply w-12 h-12 rounded-full border-2 flex items-center justify-center text-sm font-medium mb-2 relative z-10;
  @apply bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700;
}

.upload-workflow-page__step--active .upload-workflow-page__step-indicator {
  @apply bg-primary-600 border-primary-600 text-white;
}

.upload-workflow-page__step--completed .upload-workflow-page__step-indicator {
  @apply bg-green-600 border-green-600 text-white;
}

.upload-workflow-page__step--disabled .upload-workflow-page__step-indicator {
  @apply bg-neutral-100 dark:bg-neutral-700 text-neutral-400 border-neutral-200 dark:border-neutral-600;
}

.upload-workflow-page__step-check {
  @apply text-white;
}

.upload-workflow-page__step-label {
  @apply text-xs font-medium text-center;
  @apply text-neutral-600 dark:text-neutral-400;
}

.upload-workflow-page__step--active .upload-workflow-page__step-label {
  @apply text-primary-600 dark:text-primary-400;
}

.upload-workflow-page__step--completed .upload-workflow-page__step-label {
  @apply text-green-600 dark:text-green-400;
}

.upload-workflow-page__content {
  @apply flex-1 p-6;
}

.upload-workflow-page__step-content {
  @apply max-w-4xl mx-auto;
}

.upload-workflow-page__global-error {
  @apply fixed bottom-4 right-4 z-50 max-w-md;
}

.upload-workflow-page__loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.upload-workflow-page__loading-content {
  @apply bg-white dark:bg-neutral-800 rounded-lg p-6 flex flex-col items-center space-y-4;
}

.upload-workflow-page__loading-text {
  @apply text-sm text-neutral-600 dark:text-neutral-400;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .upload-workflow-page__steps {
    @apply flex-col space-y-4;
  }

  .upload-workflow-page__step:not(:last-child)::after {
    @apply hidden;
  }

  .upload-workflow-page__content {
    @apply p-4;
  }
}
</style>






