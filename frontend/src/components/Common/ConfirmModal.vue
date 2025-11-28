<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel
              class="w-full max-w-md transform overflow-hidden rounded-2xl 
                     bg-white dark:bg-neutral-800 shadow-2xl transition-all"
            >
              <!-- Header with Icon -->
              <div class="p-6 pb-0">
                <div class="flex items-start gap-4">
                  <!-- Icon -->
                  <div
                    class="flex-shrink-0 flex items-center justify-center w-12 h-12 rounded-xl"
                    :class="iconClasses"
                  >
                    <!-- Warning icon for danger -->
                    <svg v-if="confirmVariant === 'danger'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <!-- Question icon for primary -->
                    <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  
                  <!-- Content -->
                  <div class="flex-1">
                    <DialogTitle class="text-lg font-semibold text-neutral-900 dark:text-white">
                      {{ title }}
                    </DialogTitle>
                    <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
                      {{ message }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Footer -->
              <div class="flex items-center justify-end gap-3 p-6 pt-5">
                <button
                  class="px-4 py-2.5 text-sm font-medium rounded-xl
                         text-neutral-700 dark:text-neutral-300
                         hover:bg-neutral-100 dark:hover:bg-neutral-700
                         transition-colors"
                  @click="handleClose"
                >
                  {{ cancelText }}
                </button>
                <button
                  class="px-5 py-2.5 text-sm font-medium rounded-xl
                         text-white transition-colors"
                  :class="confirmButtonClasses"
                  @click="handleConfirm"
                >
                  {{ confirmText }}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionRoot,
  TransitionChild,
} from '@headlessui/vue'

interface Props {
  isOpen: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  confirmVariant?: 'primary' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: 'Подтвердить',
  cancelText: 'Отмена',
  confirmVariant: 'primary',
})

const emit = defineEmits<{
  close: []
  confirm: []
}>()

const iconClasses = computed(() => {
  if (props.confirmVariant === 'danger') {
    return 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
  }
  return 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
})

const confirmButtonClasses = computed(() => {
  if (props.confirmVariant === 'danger') {
    return 'bg-red-600 hover:bg-red-700'
  }
  return 'bg-primary-600 hover:bg-primary-700'
})

function handleClose() {
  emit('close')
}

function handleConfirm() {
  emit('confirm')
}
</script>

