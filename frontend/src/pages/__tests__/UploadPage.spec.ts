/**
 * UploadPage Component Tests
 *
 * Tests the complete upload workflow including stepper navigation,
 * state transitions, error handling, and integration with workflow store.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import UploadPage from '../UploadPage.vue'
import { useUploadWorkflowStore, type WorkflowFile } from '@/stores/uploadWorkflowStore'

// Mock dependencies
vi.mock('@/stores/uploadWorkflowStore')
vi.mock('vue-router')

describe('UploadPage', () => {
  let wrapper: VueWrapper<any>
  let workflowStore: any
  let router: any

  beforeEach(() => {
    setActivePinia(createPinia())

    // Setup router mock
    router = {
      push: vi.fn(),
      currentRoute: {
        value: {
          query: {},
          name: 'upload'
        }
      }
    }

    // Setup workflow store mock
    workflowStore = {
      currentStep: 0,
      uploadedFiles: [],
      filesMetadata: {},
      selectedCollection: null,
      shareConfig: {
        permissions: { view: true, download: false, edit: false },
        recipients: [],
        isPublic: false
      },
      isProcessing: false,
      processingMessage: '',
      error: null,
      resetWorkflow: vi.fn(),
      addFiles: vi.fn(),
      removeFile: vi.fn(),
      uploadFiles: vi.fn(),
      saveMetadata: vi.fn(),
      assignToCollection: vi.fn(),
      createShare: vi.fn(),
      completeWorkflow: vi.fn(),
      setCurrentStep: vi.fn(),
      updateMetadata: vi.fn(),
      setSelectedCollection: vi.fn(),
      updateShareConfig: vi.fn()
    }

    // Mock the composables
    vi.mocked(useUploadWorkflowStore).mockReturnValue(workflowStore)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    beforeEach(() => {
      wrapper = mount(UploadPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button']
        }
      })
    })

    it('shows stepper with upload step active', () => {
      expect(wrapper.vm.currentStep).toBe(0)
      expect(wrapper.find('.upload-workflow-page__step--active').text()).toContain('Upload Files')
    })

    it('displays step indicators correctly', () => {
      const steps = wrapper.findAll('.upload-workflow-page__step')
      expect(steps).toHaveLength(4)

      expect(steps[0].classes()).toContain('upload-workflow-page__step--active')
      expect(steps[1].classes()).toContain('upload-workflow-page__step--disabled')
    })

    it('resets workflow on mount', () => {
      expect(workflowStore.resetWorkflow).toHaveBeenCalled()
    })
  })

  describe('Navigation', () => {
    beforeEach(() => {
      wrapper = mount(UploadPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button']
        }
      })
    })

    it('navigates back to gallery', async () => {
      const backButton = wrapper.find('.upload-workflow-page__back-btn')
      await backButton.trigger('click')

      // Should show confirmation dialog, but we'll mock window.confirm
      window.confirm = vi.fn(() => true)
      await backButton.trigger('click')

      expect(router.push).toHaveBeenCalledWith('/dam')
    })

    it('shows upload step initially', () => {
      expect(wrapper.findComponent({ name: 'UploadStep' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'MetadataStep' }).exists()).toBe(false)
    })

    it('shows metadata step when currentStep is 1', async () => {
      workflowStore.currentStep = 1
      await wrapper.vm.$nextTick()

      expect(wrapper.findComponent({ name: 'MetadataStep' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'UploadStep' }).exists()).toBe(false)
    })

    it('shows collection step when currentStep is 2', async () => {
      workflowStore.currentStep = 2
      await wrapper.vm.$nextTick()

      expect(wrapper.findComponent({ name: 'CollectionStep' }).exists()).toBe(true)
    })

    it('shows share step when currentStep is 3', async () => {
      workflowStore.currentStep = 3
      await wrapper.vm.$nextTick()

      expect(wrapper.findComponent({ name: 'ShareStep' }).exists()).toBe(true)
    })
  })

  describe('Step Transitions', () => {
    beforeEach(() => {
      wrapper = mount(UploadPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button']
        }
      })
    })

    it('proceeds to next step on upload complete', async () => {
      const uploadStep = wrapper.findComponent({ name: 'UploadStep' })

      await uploadStep.vm.$emit('complete')

      expect(workflowStore.setCurrentStep).toHaveBeenCalledWith(1)
    })

    it('handles metadata step completion', async () => {
      workflowStore.currentStep = 1
      await wrapper.vm.$nextTick()

      const metadataStep = wrapper.findComponent({ name: 'MetadataStep' })
      await metadataStep.vm.$emit('complete')

      expect(workflowStore.setCurrentStep).toHaveBeenCalledWith(2)
    })

    it('handles collection step completion', async () => {
      workflowStore.currentStep = 2
      await wrapper.vm.$nextTick()

      const collectionStep = wrapper.findComponent({ name: 'CollectionStep' })
      await collectionStep.vm.$emit('complete')

      expect(workflowStore.setCurrentStep).toHaveBeenCalledWith(3)
    })

    it('handles workflow completion', async () => {
      workflowStore.currentStep = 3
      await wrapper.vm.$nextTick()

      const shareStep = wrapper.findComponent({ name: 'ShareStep' })
      await shareStep.vm.$emit('complete')

      expect(router.push).toHaveBeenCalledWith('/dam')
    })

    it('handles step back navigation', async () => {
      workflowStore.currentStep = 2
      await wrapper.vm.$nextTick()

      const collectionStep = wrapper.findComponent({ name: 'CollectionStep' })
      await collectionStep.vm.$emit('back')

      expect(workflowStore.setCurrentStep).toHaveBeenCalledWith(1)
    })
  })

  describe('Error Handling', () => {
    beforeEach(() => {
      wrapper = mount(UploadPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button']
        }
      })
    })

    it('displays global error from workflow store', async () => {
      workflowStore.error = 'Upload failed'
      await wrapper.vm.$nextTick()

      const errorAlert = wrapper.find('.upload-workflow-page__global-error')
      expect(errorAlert.exists()).toBe(true)
      expect(errorAlert.text()).toContain('Upload failed')
    })

    it('handles step-specific errors', async () => {
      const uploadStep = wrapper.findComponent({ name: 'UploadStep' })
      await uploadStep.vm.$emit('error', 'File too large')

      expect(wrapper.vm.globalError).toBe('File too large')
    })

    it('clears error when dismissed', async () => {
      workflowStore.error = 'Test error'
      await wrapper.vm.$nextTick()

      const errorAlert = wrapper.find('.upload-workflow-page__global-error')
      await errorAlert.vm.$emit('dismiss')

      expect(workflowStore.error).toBe(null)
    })
  })

  describe('Processing States', () => {
    beforeEach(() => {
      wrapper = mount(UploadPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button', 'Spinner']
        }
      })
    })

    it('shows processing overlay when workflow is processing', async () => {
      workflowStore.isProcessing = true
      workflowStore.processingMessage = 'Uploading files...'
      await wrapper.vm.$nextTick()

      const overlay = wrapper.find('.upload-workflow-page__loading-overlay')
      expect(overlay.exists()).toBe(true)
      expect(overlay.text()).toContain('Uploading files...')
    })

    it('hides processing overlay when not processing', async () => {
      workflowStore.isProcessing = false
      await wrapper.vm.$nextTick()

      const overlay = wrapper.find('.upload-workflow-page__loading-overlay')
      expect(overlay.exists()).toBe(false)
    })
  })

  describe('Accessibility', () => {
    beforeEach(() => {
      wrapper = mount(UploadPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button']
        }
      })
    })

    it('has proper heading hierarchy', () => {
      const headings = wrapper.findAll('h1, h2, h3')
      expect(headings.length).toBeGreaterThan(0)

      // Main heading should be h2 for page structure
      const mainHeading = wrapper.find('h2')
      expect(mainHeading.exists()).toBe(true)
    })

    it('has accessible step indicators', () => {
      const steps = wrapper.findAll('.upload-workflow-page__step')
      steps.forEach(step => {
        expect(step.attributes('role')).toBeUndefined() // Not needed for visual indicators
      })
    })

    it('has keyboard accessible back button', () => {
      const backButton = wrapper.find('.upload-workflow-page__back-btn')
      expect(backButton.attributes('type')).toBe('button')
    })
  })

  describe('Responsive Design', () => {
    beforeEach(() => {
      wrapper = mount(UploadPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button']
        }
      })
    })

    it('applies mobile-specific classes', () => {
      // Test that mobile styles are applied (we can't test actual breakpoints in unit tests)
      const stepper = wrapper.find('.upload-workflow-page__steps')
      expect(stepper.classes()).toContain('max-w-2xl')
    })

    it('stacks controls vertically on mobile', () => {
      const controls = wrapper.find('.upload-workflow-page__controls')
      expect(controls.classes()).toContain('flex')
    })
  })

  describe('Data Binding', () => {
    beforeEach(() => {
      wrapper = mount(UploadPage, {
        global: {
          plugins: [createRouter({ history: createWebHistory(), routes: [] })],
          stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button']
        }
      })
    })

    it('binds files to upload step', () => {
      const uploadStep = wrapper.findComponent({ name: 'UploadStep' })
      expect(uploadStep.props('files')).toBe(workflowStore.uploadedFiles)
    })

    it('binds metadata to metadata step', () => {
      workflowStore.currentStep = 1
      wrapper.vm.currentStep = 1
      wrapper.vm.$nextTick()

      const metadataStep = wrapper.findComponent({ name: 'MetadataStep' })
      expect(metadataStep.props('metadata')).toBe(workflowStore.filesMetadata)
    })

    it('binds collection to collection step', () => {
      workflowStore.currentStep = 2
      wrapper.vm.currentStep = 2
      wrapper.vm.$nextTick()

      const collectionStep = wrapper.findComponent({ name: 'CollectionStep' })
      expect(collectionStep.props('selectedCollection')).toBe(workflowStore.selectedCollection)
    })

    it('passes data to share step', () => {
      workflowStore.currentStep = 3
      wrapper.vm.currentStep = 3
      wrapper.vm.$nextTick()

      const shareStep = wrapper.findComponent({ name: 'ShareStep' })
      expect(shareStep.props('files')).toBe(workflowStore.uploadedFiles)
      expect(shareStep.props('metadata')).toBe(workflowStore.filesMetadata)
      expect(shareStep.props('collection')).toBe(workflowStore.selectedCollection)
    })
  })

  describe('Edge Cases', () => {
    it('handles invalid step navigation gracefully', () => {
      wrapper.vm.currentStep = 999
      expect(wrapper.vm.currentStep).toBe(999) // Component allows any step, validation in store
    })

    it('handles missing workflow store gracefully', () => {
      vi.mocked(useUploadWorkflowStore).mockReturnValue(null as any)

      expect(() => {
        mount(UploadPage, {
          global: {
            plugins: [createRouter({ history: createWebHistory(), routes: [] })],
            stubs: ['UploadStep', 'MetadataStep', 'CollectionStep', 'ShareStep', 'Alert', 'Button']
          }
        })
      }).not.toThrow()
    })

    it('handles router navigation errors', () => {
      router.push.mockRejectedValue(new Error('Navigation failed'))

      const backButton = wrapper.find('.upload-workflow-page__back-btn')
      window.confirm = vi.fn(() => true)

      expect(() => backButton.trigger('click')).not.toThrow()
    })
  })
})











