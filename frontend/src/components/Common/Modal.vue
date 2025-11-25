<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-normal ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-normal ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>

        <!-- Modal container -->
        <div class="flex min-h-full items-center justify-center p-4">
          <Transition
            enter-active-class="transition-all duration-normal ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-4"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition-all duration-normal ease-in"
            leave-from-class="opacity-100 scale-100 translate-y-0"
            leave-to-class="opacity-0 scale-95 translate-y-4"
          >
            <div
              v-if="isOpen"
              :class="modalClasses"
              @click.stop
            >
              <!-- Header -->
              <div v-if="title || $slots.header" class="flex items-center justify-between px-6 py-4 border-b border-neutral-300 dark:border-neutral-300">
                <h3 v-if="title" class="text-xl font-semibold text-neutral-900 dark:text-neutral-900">
                  {{ title }}
                </h3>
                <slot name="header" />
                <button
                  v-if="closable"
                  @click="handleClose"
                  class="ml-4 text-neutral-600 hover:text-neutral-900 dark:text-neutral-600 dark:hover:text-neutral-900 transition-colors"
                  aria-label="Close"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Body -->
              <div class="px-6 py-4">
                <slot />
              </div>

              <!-- Footer -->
              <div v-if="$slots.footer" class="flex items-center justify-end gap-3 px-6 py-4 border-t border-neutral-300 dark:border-neutral-300">
                <slot name="footer" />
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'

interface Props {
  isOpen: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closable?: boolean
  closeOnBackdrop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  closable: true,
  closeOnBackdrop: true
})

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  close: []
}>()

const modalClasses = computed(() => {
  const base = 'relative bg-neutral-0 dark:bg-neutral-0 rounded-lg shadow-xl w-full max-h-[90vh] overflow-hidden flex flex-col'
  
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4'
  }
  
  return `${base} ${sizes[props.size]}`
})

function handleClose() {
  emit('update:isOpen', false)
  emit('close')
}

function handleBackdropClick() {
  if (props.closeOnBackdrop) {
    handleClose()
  }
}

// Close on Escape key
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && props.closable) {
        handleClose()
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }
})
</script>


