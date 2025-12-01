<template>
  <Modal
    :isOpen="isOpen"
    title="Upload assets"
    size="lg"
    @close="handleClose"
    :aria-describedby="'upload-status'"
  >
    <div class="upload-modal__container">
      <div
        class="upload-modal__drop-zone"
        :class="{ 'upload-modal__drop-zone--active': isDragging }"
        role="region"
        aria-label="Drag and drop files here"
        tabindex="0"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="handleDrop"
        @keydown.enter.prevent="triggerFileDialog"
        @keydown.space.prevent="triggerFileDialog"
      >
        <i class="icon icon-upload-cloud" aria-hidden="true" />
        <p class="upload-modal__drop-text">
          Drag files here or
          <button
            type="button"
            class="upload-modal__browse-btn"
            @click="triggerFileDialog"
          >
            browse
          </button>
        </p>
        <p class="upload-modal__drop-hint">Max 500MB per file, 2GB total</p>
        <input
          ref="fileInput"
          type="file"
          multiple
          :accept="acceptString"
          class="upload-modal__file-input"
          aria-hidden="true"
          @change="handleFileSelect"
        />
      </div>

      <p id="upload-status" class="sr-only" role="status">
        {{ screenReaderStatus }}
      </p>

      <div v-if="files.length > 0" class="upload-modal__files">
        <div
          v-for="(file, idx) in files"
          :key="file.hash"
          class="upload-modal__file-item"
        >
          <div class="upload-modal__file-info">
            <i :class="['icon', getFileIcon(file.type)]" aria-hidden="true" />
            <div class="upload-modal__file-details">
              <p class="upload-modal__file-name">{{ file.name }}</p>
              <p class="upload-modal__file-size">{{ formatBytes(file.size) }}</p>
            </div>
          </div>

          <div :class="['upload-modal__status', `upload-modal__status--${file.status}`]">
            {{ file.status }}
          </div>

          <div class="upload-modal__progress-wrapper" v-if="file.status === 'uploading'">
            <div class="upload-modal__progress-bar" role="progressbar" :aria-valuenow="file.progress" aria-valuemin="0" aria-valuemax="100">
              <div
                class="upload-modal__progress-fill"
                :style="{ width: file.progress + '%' }"
              />
            </div>
            <p class="upload-modal__progress-text">
              {{ file.progress }}% • {{ file.speed }} • ETA {{ file.eta }}
            </p>
          </div>

          <p v-if="file.error" class="upload-modal__error-message">
            ⚠️ {{ file.error }}
          </p>

          <div class="upload-modal__file-actions">
            <button
              v-if="file.status === 'failed'"
              type="button"
              class="upload-modal__btn-small"
              @click="retryFile(idx)"
            >
              Retry
            </button>
            <button
              v-if="['pending', 'uploading'].includes(file.status)"
              type="button"
              class="upload-modal__btn-small upload-modal__btn-small--cancel"
              @click="cancelFile(idx)"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>

      <div v-if="validationErrors.length > 0" class="upload-modal__validation-errors">
        <p
          v-for="(error, idx) in validationErrors"
          :key="idx"
          class="upload-modal__error-item"
        >
          🚫 {{ error }}
        </p>
      </div>

      <div v-if="isUploading" class="upload-modal__overall-progress">
        <p>Uploading {{ filesUploading }}/{{ files.length }} files...</p>
        <div class="upload-modal__progress-bar upload-modal__progress-bar--overall">
          <div
            class="upload-modal__progress-fill"
            :style="{ width: overallProgress + '%' }"
          />
        </div>
      </div>

      <div v-if="uploadComplete && !hasErrors" class="upload-modal__success">
        <i class="icon icon-check-circle" aria-hidden="true" />
        <p>All files uploaded successfully.</p>
        <div class="upload-modal__success-actions">
          <Button variant="secondary" @click="resetState(false)">Upload more</Button>
          <Button variant="ghost" @click="viewGallery">View gallery</Button>
        </div>
      </div>

      <div class="upload-modal__footer">
        <Button variant="secondary" @click="handleClose">Close</Button>
        <Button
          v-if="!isUploading && !uploadComplete"
          variant="primary"
          :disabled="files.length === 0 || validationErrors.length > 0"
          @click="startUpload"
        >
          Upload {{ files.length }} {{ files.length === 1 ? 'file' : 'files' }}
        </Button>
        <Button v-if="isUploading" variant="secondary" @click="cancelAllUploads">
          Cancel all
        </Button>
        <Button
          v-if="uploadComplete && hasErrors"
          variant="primary"
          @click="retryFailed"
        >
          Retry failed
        </Button>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import {
  ref,
  computed,
  watch,
  onBeforeUnmount
} from 'vue'
import type { AxiosProgressEvent } from 'axios'
import { useRouter } from 'vue-router'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import { useAssetStore } from '@/stores/assetStore'
import { useUIStore } from '@/stores/uiStore'
import { extractErrorCode } from '@/utils/errorHandling'
import { formatApiError } from '@/utils/errors'
import type { FileUploadProgress } from '@/types/upload'

const props = defineProps<{
  isOpen: boolean
  collectionId?: number
}>()

const emit = defineEmits<{
  close: []
  success: [File[]]
}>()

const router = useRouter()
const uiStore = useUIStore()
const assetStore = useAssetStore()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const isUploading = ref(false)
const uploadComplete = ref(false)
const validationErrors = ref<string[]>([])
const files = ref<FileUploadProgress[]>([])
const autoCloseTimer = ref<number | null>(null)

const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.mov', '.mp4', '.avi']
const ALLOWED_MIME_PREFIXES = ['image/', 'video/']
const MAX_FILE_SIZE = 500 * 1024 * 1024
const MAX_TOTAL_SIZE = 2 * 1024 * 1024 * 1024

const acceptString = computed(() => ALLOWED_EXTENSIONS.join(','))

const filesUploading = computed(() =>
  files.value.filter((file) => file.status === 'uploading').length
)

const overallProgress = computed(() => {
  const totalBytes = files.value.reduce((acc, file) => acc + file.size, 0)
  const uploadedBytes = files.value.reduce(
    (acc, file) => acc + (file.uploadedBytes || 0),
    0
  )
  return totalBytes > 0 ? Math.round((uploadedBytes / totalBytes) * 100) : 0
})

const hasErrors = computed(() =>
  files.value.some((file) => file.status === 'failed')
)

const screenReaderStatus = computed(() =>
  `${files.value.length} file${files.value.length === 1 ? '' : 's'} ready to upload`
)

const triggerFileDialog = (): void => {
  fileInput.value?.click()
}

const handleDrop = (event: DragEvent): void => {
  isDragging.value = false
  const dropped = event.dataTransfer?.files
  if (dropped) {
    addFiles(Array.from(dropped))
  }
}

const handleFileSelect = (event: Event): void => {
  const input = event.target as HTMLInputElement
  if (input.files) {
    addFiles(Array.from(input.files))
    input.value = ''
  }
}

const addFiles = (newFiles: File[]): void => {
  validationErrors.value = []
  const totalExisting = files.value.reduce((acc, file) => acc + file.size, 0)
  let runningTotal = totalExisting

  for (const file of newFiles) {
    const hash = `${file.name}-${file.size}`
    if (files.value.some((item) => item.hash === hash && item.status === 'success')) {
      continue
    }

    const validationMessage = validateFile(file, runningTotal)
    runningTotal += file.size

    if (validationMessage) {
      validationErrors.value.push(validationMessage)
      continue
    }

    files.value.push({
      file,
      hash,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0,
      uploadedBytes: 0,
      speed: '0 MB/s',
      eta: '--',
      error: null
    })
  }

  if (validationErrors.value.length > 0) {
    uiStore.addNotification({
      type: 'warning',
      message: `${validationErrors.value.length} file(s) validation failed`,
      duration: 4000
    })
  }
}

const validateFile = (file: File, currentTotal: number): string | null => {
  if (file.size > MAX_FILE_SIZE) {
    return `${file.name} exceeds ${formatBytes(MAX_FILE_SIZE)} limit`
  }
  if (currentTotal + file.size > MAX_TOTAL_SIZE) {
    return 'Combined upload exceeds 2GB limit'
  }
  const ext = `.${file.name.split('.').pop()?.toLowerCase() || ''}`
  const mimeValid = ALLOWED_MIME_PREFIXES.some((prefix) =>
    file.type.startsWith(prefix)
  )
  const extensionValid = ALLOWED_EXTENSIONS.includes(ext)
  if (!mimeValid && !extensionValid) {
    return `${file.name} is not an accepted file type`
  }
  return null
}

const startUpload = async (): Promise<void> => {
  if (!files.value.length) return
  isUploading.value = true
  uploadComplete.value = false
  validationErrors.value = []

  for (const fileItem of files.value) {
    if (fileItem.status !== 'pending') continue
    fileItem.abortController = new AbortController()
    fileItem.startedAt = Date.now()
    try {
      fileItem.status = 'uploading'
      await uploadFile(fileItem)
      fileItem.status = 'success'
      fileItem.speed = '0 MB/s'
      fileItem.eta = '0s'
    } catch (error) {
      if (fileItem.abortController?.signal.aborted) {
        fileItem.status = 'cancelled'
        fileItem.error = 'Upload canceled'
      } else {
        fileItem.status = 'failed'
        fileItem.error = formatUploadError(error)
      }
    }
  }

  isUploading.value = false
  uploadComplete.value = true

  const successCount = files.value.filter((file) => file.status === 'success').length
  if (successCount) {
    uiStore.addNotification({
      type: 'success',
      message: `Uploaded ${successCount} file${successCount === 1 ? '' : 's'}`,
      duration: 3000
    })
    emit(
      'success',
      files.value.filter((file) => file.status === 'success').map((file) => file.file)
    )
  }
}

const uploadFile = async (fileItem: FileUploadProgress): Promise<void> => {
  const formData = new FormData()
  formData.append('file', fileItem.file)
  if (props.collectionId) {
    formData.append('collection_id', String(props.collectionId))
  }

  await assetStore.uploadAsset(formData, {
    signal: fileItem.abortController?.signal,
    onUploadProgress: (event) => handleProgress(fileItem, event)
  })
}

const handleProgress = (
  fileItem: FileUploadProgress,
  event: AxiosProgressEvent
): void => {
  const now = Date.now()
  const total = event.total ?? fileItem.size
  const deltaTime =
    (now - (fileItem.lastProgressAt || fileItem.startedAt || now)) / 1000 || 0.1
  const loaded = event.loaded ?? fileItem.uploadedBytes ?? 0
  const prevUploaded = fileItem.uploadedBytes || 0
  const deltaBytes = loaded - prevUploaded
  fileItem.uploadedBytes = loaded
  fileItem.progress = Math.min(100, Math.round((loaded / total) * 100))
  const speedBytes = deltaBytes / deltaTime
  const speedMb = Math.max(speedBytes / (1024 * 1024), 0.01)
  fileItem.speed = `${speedMb.toFixed(2)} MB/s`
  const remainingBytes = total - loaded
  const etaSeconds = speedBytes > 0 ? Math.ceil(remainingBytes / speedBytes) : 0
  fileItem.eta = etaSeconds > 0 ? formatDuration(etaSeconds) : '0s'
  fileItem.lastProgressAt = now
}

const retryFile = async (index: number): Promise<void> => {
  const fileItem = files.value[index]
  if (!fileItem) return
  fileItem.status = 'pending'
  fileItem.progress = 0
  fileItem.uploadedBytes = 0
  fileItem.error = null
  await startUpload()
}

const cancelFile = (index: number): void => {
  const fileItem = files.value[index]
  if (!fileItem) return
  fileItem.abortController?.abort()
  if (['pending', 'uploading'].includes(fileItem.status)) {
    fileItem.status = 'cancelled'
    fileItem.error = 'Cancelled by user'
  }
}

const cancelAllUploads = (): void => {
  files.value.forEach((file) => {
    file.abortController?.abort()
    if (['pending', 'uploading'].includes(file.status)) {
      file.status = 'cancelled'
      file.error = 'Cancelled by user'
    }
  })
  isUploading.value = false
}

const retryFailed = async (): Promise<void> => {
  files.value = files.value.map((file) =>
    file.status === 'failed'
      ? {
          ...file,
          status: 'pending',
          progress: 0,
          uploadedBytes: 0,
          error: null
        }
      : file
  )
  await startUpload()
}

const handleClose = (): void => {
  resetState()
  emit('close')
}

const resetState = (keepOpen = false): void => {
  isUploading.value = false
  uploadComplete.value = false
  validationErrors.value = []
  files.value = []
  isDragging.value = false
  clearTimeout(autoCloseTimer.value ?? 0)
  autoCloseTimer.value = null
  if (!keepOpen && props.isOpen) {
    emit('close')
  }
}

const viewGallery = (): void => {
  router.push('/dam/gallery')
  handleClose()
}

const getFileIcon = (type: string): string => {
  if (type.startsWith('image/')) return 'icon-image'
  if (type.startsWith('video/')) return 'icon-video'
  if (type.includes('pdf')) return 'icon-file-pdf'
  if (type.includes('doc')) return 'icon-file-doc'
  return 'icon-file'
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`
}

const formatDuration = (seconds: number): string => {
  if (seconds <= 0) return '0s'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
}

const formatUploadError = (error: unknown): string => {
  const message = formatApiError(error)
  const code = extractErrorCode(error)
  return code ? `${code}: ${message}` : message
}

watch(
  () => uploadComplete.value,
  (complete) => {
    if (complete && !hasErrors.value) {
      autoCloseTimer.value = window.setTimeout(() => handleClose(), 3000)
    }
  }
)

onBeforeUnmount(() => {
  clearTimeout(autoCloseTimer.value ?? 0)
})

watch(
  () => props.isOpen,
  (open) => {
    if (!open) {
      resetState()
    }
  }
)
</script>

<style scoped>
.upload-modal__container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 480px;
}

.upload-modal__drop-zone {
  min-height: 220px;
  border: 2px dashed var(--color-border, #d1d5db);
  border-radius: 14px;
  background: var(--color-surface, #ffffff);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 150ms ease;
}

.upload-modal__drop-zone--active {
  border-color: var(--color-primary, #2563eb);
  background: rgba(37, 99, 235, 0.08);
}

.upload-modal__drop-text {
  margin: 0;
  font-size: 1rem;
  color: var(--color-text, #111827);
}

.upload-modal__browse-btn {
  border: none;
  background: none;
  color: var(--color-primary, #2563eb);
  font-weight: 600;
  cursor: pointer;
  margin-left: 4px;
}

.upload-modal__drop-hint {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.upload-modal__files {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
}

.upload-modal__file-item {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--color-border, #e5e7eb);
  background: var(--color-surface, #fff);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-modal__file-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.upload-modal__file-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.upload-modal__file-name {
  margin: 0;
  font-weight: 600;
  color: var(--color-text, #111827);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-modal__file-size {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary, #6b7280);
}

.upload-modal__status {
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.upload-modal__status--pending {
  background: #f8fafc;
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.upload-modal__status--uploading {
  background: #eef2ff;
  color: #4c1d95;
  border: 1px solid rgba(76, 29, 149, 0.3);
}

.upload-modal__status--success {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid rgba(4, 120, 87, 0.3);
}

.upload-modal__status--failed,
.upload-modal__status--cancelled {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid rgba(185, 28, 28, 0.3);
}

.upload-modal__progress-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.upload-modal__progress-bar {
  width: 100%;
  height: 6px;
  background: var(--color-border, #e5e7eb);
  border-radius: 999px;
  overflow: hidden;
}

.upload-modal__progress-bar--overall {
  height: 8px;
}

.upload-modal__progress-fill {
  height: 100%;
  background: var(--color-primary, #2563eb);
  transition: width 0.3s ease;
}

.upload-modal__progress-text {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.upload-modal__error-message {
  margin: 0;
  font-size: 0.8rem;
  color: #b91c1c;
}

.upload-modal__validation-errors {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.upload-modal__error-item {
  margin: 0;
  font-size: 0.85rem;
  color: #b91c1c;
}

.upload-modal__footer {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
}

.upload-modal__success {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid var(--color-success, #22c55e);
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success, #22c55e);
}

.upload-modal__success-actions {
  display: flex;
  gap: 8px;
}

.upload-modal__file-input {
  position: absolute;
  left: -9999px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

@media (max-width: 768px) {
  .upload-modal__container {
    width: 100%;
    min-width: auto;
  }
}
</style>

