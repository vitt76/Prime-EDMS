/**
 * Upload Workflow Store
 *
 * Manages the state of the multi-step upload workflow:
 * - File uploads with progress tracking
 * - Metadata collection
 * - Collection assignment
 * - Sharing configuration
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { uploadService } from '@/services/uploadService'
import { assetService } from '@/services/assetService'
import { collectionsService } from '@/services/collectionsService'
import { shareService } from '@/services/shareService'
import { useUIStore } from '@/stores/uiStore'

// Types
export interface WorkflowFile {
  id: string
  file: File
  name: string
  size: number
  type: string
  uploadProgress: number
  uploadStatus: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
  preview?: string
  assetId?: string
}

export interface FileMetadata {
  [fileId: string]: Record<string, any>
}

export interface Collection {
  id: string
  name: string
  path: string[]
  type: 'folder' | 'collection'
  parentId?: string
}

export interface ShareConfig {
  permissions: {
    view: boolean
    download: boolean
    edit: boolean
  }
  expiration?: Date
  password?: string
  recipients: string[]
  isPublic: boolean
}

export interface WorkflowState {
  currentStep: number
  uploadedFiles: WorkflowFile[]
  filesMetadata: FileMetadata
  selectedCollection: Collection | null
  shareConfig: ShareConfig
  isProcessing: boolean
  processingMessage: string
  error: string | null
}

export const useUploadWorkflowStore = defineStore(
  'uploadWorkflow',
  () => {
    // State
    const currentStep = ref(0)
    const uploadedFiles = ref<WorkflowFile[]>([])
    const filesMetadata = ref<FileMetadata>({})
    const selectedCollection = ref<Collection | null>(null)
    const shareConfig = ref<ShareConfig>({
      permissions: {
        view: true,
        download: false,
        edit: false
      },
      recipients: [],
      isPublic: false
    })
    const isProcessing = ref(false)
    const processingMessage = ref('')
    const error = ref<string | null>(null)

    // Getters
    const completedFiles = computed(() =>
      uploadedFiles.value.filter(f => f.uploadStatus === 'completed')
    )

    const failedFiles = computed(() =>
      uploadedFiles.value.filter(f => f.uploadStatus === 'error')
    )

    const totalProgress = computed(() => {
      if (uploadedFiles.value.length === 0) return 0
      const totalProgress = uploadedFiles.value.reduce((sum, file) => sum + file.uploadProgress, 0)
      return Math.round(totalProgress / uploadedFiles.value.length)
    })

    const canProceedToMetadata = computed(() =>
      completedFiles.value.length > 0
    )

    const canProceedToCollection = computed(() =>
      Object.keys(filesMetadata.value).length > 0
    )

    const canProceedToShare = computed(() =>
      selectedCollection.value !== null
    )

    // Actions
    function resetWorkflow() {
      currentStep.value = 0
      uploadedFiles.value = []
      filesMetadata.value = {}
      selectedCollection.value = null
      shareConfig.value = {
        permissions: {
          view: true,
          download: false,
          edit: false
        },
        recipients: [],
        isPublic: false
      }
      isProcessing.value = false
      processingMessage.value = ''
      error.value = null
    }

    async function addFiles(files: FileList | File[]) {
      const fileArray = Array.from(files)
      const workflowFiles: WorkflowFile[] = fileArray.map(file => ({
        id: crypto.randomUUID(),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadProgress: 0,
        uploadStatus: 'pending'
      }))

      uploadedFiles.value.push(...workflowFiles)

      // Generate previews for images
      workflowFiles.forEach(generateFilePreview)
    }

    function removeFile(fileId: string) {
      const index = uploadedFiles.value.findIndex(f => f.id === fileId)
      if (index !== -1) {
        uploadedFiles.value.splice(index, 1)
        // Remove metadata for this file
        delete filesMetadata.value[fileId]
      }
    }

    function generateFilePreview(workflowFile: WorkflowFile) {
      if (workflowFile.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          workflowFile.preview = e.target?.result as string
        }
        reader.readAsDataURL(workflowFile.file)
      }
    }

    async function uploadFiles() {
      if (uploadedFiles.value.length === 0) return

      isProcessing.value = true
      processingMessage.value = 'Uploading files...'
      error.value = null

      try {
        const uploadPromises = uploadedFiles.value.map(async (workflowFile) => {
          if (workflowFile.uploadStatus === 'completed') return

          workflowFile.uploadStatus = 'uploading'

          try {
            const result = await uploadService.uploadFile(workflowFile.file, {
              onProgress: (progress) => {
                workflowFile.uploadProgress = progress
              }
            })

            workflowFile.uploadStatus = 'completed'
            workflowFile.assetId = result.assetId
            workflowFile.uploadProgress = 100
          } catch (uploadError: any) {
            workflowFile.uploadStatus = 'error'
            workflowFile.error = uploadError.message || 'Upload failed'
            throw uploadError
          }
        })

        await Promise.allSettled(uploadPromises)

        // Check if all files were uploaded successfully
        const allSuccessful = uploadedFiles.value.every(f => f.uploadStatus === 'completed')
        if (!allSuccessful) {
          const failedCount = failedFiles.value.length
          throw new Error(`${failedCount} file(s) failed to upload`)
        }

      } catch (err: any) {
        error.value = err.message || 'Upload failed'
        throw err
      } finally {
        isProcessing.value = false
        processingMessage.value = ''
      }
    }

    async function saveMetadata() {
      if (Object.keys(filesMetadata.value).length === 0) return

      isProcessing.value = true
      processingMessage.value = 'Saving metadata...'
      error.value = null

      try {
        const metadataPromises = Object.entries(filesMetadata.value).map(async ([fileId, metadata]) => {
          const workflowFile = uploadedFiles.value.find(f => f.id === fileId)
          if (!workflowFile?.assetId) return

          await assetService.updateAssetMetadata(workflowFile.assetId, metadata)
        })

        await Promise.all(metadataPromises)
      } catch (err: any) {
        error.value = err.message || 'Failed to save metadata'
        throw err
      } finally {
        isProcessing.value = false
        processingMessage.value = ''
      }
    }

    async function assignToCollection() {
      if (!selectedCollection.value || completedFiles.value.length === 0) return

      isProcessing.value = true
      processingMessage.value = 'Assigning to collection...'
      error.value = null

      try {
        const assetIds = completedFiles.value
          .map(f => f.assetId)
          .filter(Boolean) as string[]

        await collectionService.addAssetsToCollection(
          selectedCollection.value.id,
          assetIds
        )
      } catch (err: any) {
        error.value = err.message || 'Failed to assign to collection'
        throw err
      } finally {
        isProcessing.value = false
        processingMessage.value = ''
      }
    }

    async function createShare() {
      if (completedFiles.value.length === 0) return

      isProcessing.value = true
      processingMessage.value = 'Creating share links...'
      error.value = null

      try {
        const assetIds = completedFiles.value
          .map(f => f.assetId)
          .filter(Boolean) as string[]

        const shareResult = await shareService.createBulkShare(assetIds, shareConfig.value)

        // Update share config with generated links
        shareConfig.value = {
          ...shareConfig.value,
          ...shareResult
        }
      } catch (err: any) {
        error.value = err.message || 'Failed to create share links'
        throw err
      } finally {
        isProcessing.value = false
        processingMessage.value = ''
      }
    }

    async function completeWorkflow() {
      try {
        // Final processing steps
        await saveMetadata()
        await assignToCollection()
        await createShare()

        // Show success message
        const uiStore = useUIStore()
        uiStore.addNotification({
          type: 'success',
          title: 'Upload Complete',
          message: `${completedFiles.value.length} file(s) uploaded successfully`
        })

        // Reset workflow for next use
        resetWorkflow()

      } catch (err) {
        // Error already set in individual steps
        throw err
      }
    }

    function setCurrentStep(step: number) {
      currentStep.value = Math.max(0, Math.min(step, 3))
    }

    function updateMetadata(fileId: string, metadata: Record<string, any>) {
      filesMetadata.value[fileId] = { ...filesMetadata.value[fileId], ...metadata }
    }

    function setSelectedCollection(collection: Collection | null) {
      selectedCollection.value = collection
    }

    function updateShareConfig(config: Partial<ShareConfig>) {
      shareConfig.value = { ...shareConfig.value, ...config }
    }

    return {
      // State
      currentStep,
      uploadedFiles,
      filesMetadata,
      selectedCollection,
      shareConfig,
      isProcessing,
      processingMessage,
      error,

      // Getters
      completedFiles,
      failedFiles,
      totalProgress,
      canProceedToMetadata,
      canProceedToCollection,
      canProceedToShare,

      // Actions
      resetWorkflow,
      addFiles,
      removeFile,
      uploadFiles,
      saveMetadata,
      assignToCollection,
      createShare,
      completeWorkflow,
      setCurrentStep,
      updateMetadata,
      setSelectedCollection,
      updateShareConfig
    }
  },
  {
    persist: {
      paths: ['currentStep', 'filesMetadata', 'selectedCollection', 'shareConfig']
    }
  }
)
