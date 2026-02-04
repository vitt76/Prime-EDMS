<template>
  <TransitionRoot appear :show="modelValue" as="template">
    <Dialog as="div" class="relative z-50" @close="$emit('update:modelValue', false)">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-black p-2 shadow-2xl transition-all">
              <!-- Close Button -->
              <button
                @click="$emit('update:modelValue', false)"
                class="absolute right-4 top-4 z-10 rounded-full bg-white/10 p-2 text-white transition hover:bg-white/20"
                aria-label="Close video"
              >
                <XMarkIcon class="h-6 w-6" />
              </button>

              <!-- Video Container -->
              <div class="relative aspect-video w-full overflow-hidden rounded-xl bg-neutral-900">
                <div v-if="!videoLoaded && videoUrl" class="absolute inset-0 flex items-center justify-center">
                  <div class="flex flex-col items-center gap-4 text-white">
                    <div class="h-12 w-12 animate-spin rounded-full border-4 border-primary-500 border-t-transparent"></div>
                    <span class="text-sm">Loading video...</span>
                  </div>
                </div>
                
                <!-- YouTube Embed or Placeholder -->
                <iframe
                  v-if="videoUrl"
                  :src="videoUrl"
                  class="h-full w-full"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                  @load="videoLoaded = true"
                ></iframe>
                
                <!-- Placeholder when no video -->
                <div v-else class="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary-600 to-primary-800">
                  <div class="text-center text-white">
                    <PlayIcon class="mx-auto h-16 w-16 opacity-50" />
                    <p class="mt-4 text-lg font-medium">Demo video coming soon</p>
                    <p class="mt-2 text-sm opacity-70">Check back later for our product walkthrough</p>
                  </div>
                </div>
              </div>

              <!-- Video Title -->
              <div class="mt-4 px-2 pb-2 text-left">
                <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
                <p class="mt-1 text-sm text-neutral-400">{{ description }}</p>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
} from '@headlessui/vue'
import { XMarkIcon, PlayIcon } from '@heroicons/vue/24/outline'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    videoUrl?: string
    title?: string
    description?: string
  }>(),
  {
    title: 'MADDAM Product Demo',
    description: 'See how MADDAM helps teams manage digital assets efficiently'
  }
)

defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const videoLoaded = ref(false)

// Reset video loaded state when modal closes
watch(() => props.modelValue, (isOpen) => {
  if (!isOpen) {
    videoLoaded.value = false
  }
})
</script>
