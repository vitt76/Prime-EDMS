<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="div"
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
            as="div"
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
              <!-- Header -->
              <div class="flex items-center justify-between p-5 border-b border-neutral-200 dark:border-neutral-700">
                <div class="flex items-center gap-3">
                  <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900/30">
                    <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                  </div>
                  <div>
                    <DialogTitle class="text-lg font-semibold text-neutral-900 dark:text-white">
                      Добавить теги
                    </DialogTitle>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">
                      {{ selectedCount }} актив(ов) выбрано
                    </p>
                  </div>
                </div>
                <button
                  class="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 
                         text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300
                         transition-colors"
                  @click="handleClose"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Body -->
              <div class="p-5 space-y-4">
                <!-- Tag Input -->
                <div>
                  <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Введите теги
                  </label>
                  <div class="relative">
                    <input
                      ref="inputRef"
                      v-model="tagInput"
                      type="text"
                      class="w-full px-4 py-3 rounded-xl border border-neutral-300 dark:border-neutral-600
                             bg-white dark:bg-neutral-900
                             text-neutral-900 dark:text-white
                             placeholder-neutral-400
                             focus:ring-2 focus:ring-primary-500 focus:border-transparent
                             transition-all"
                      placeholder="Введите тег и нажмите Enter..."
                      @keydown.enter.prevent="addTag"
                      @keydown.tab.prevent="addTag"
                    />
                  </div>
                  <p class="mt-1.5 text-xs text-neutral-500 dark:text-neutral-400">
                    Нажмите Enter или Tab для добавления тега
                  </p>
                </div>

                <!-- Added Tags -->
                <div v-if="selectedTags.length > 0" class="flex flex-wrap gap-2">
                  <span
                    v-for="(tag, index) in selectedTags"
                    :key="index"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 
                           bg-primary-100 dark:bg-primary-900/30 
                           text-primary-700 dark:text-primary-300 
                           text-sm font-medium rounded-lg"
                  >
                    {{ tag }}
                    <button
                      class="hover:bg-primary-200 dark:hover:bg-primary-800 rounded p-0.5 transition-colors"
                      @click="removeTag(index)"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                </div>

                <!-- Suggested Tags -->
                <div>
                  <p class="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Популярные теги
                  </p>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="tag in suggestedTags"
                      :key="tag"
                      class="px-3 py-1.5 text-sm rounded-lg
                             bg-neutral-100 dark:bg-neutral-700 
                             text-neutral-700 dark:text-neutral-300
                             hover:bg-neutral-200 dark:hover:bg-neutral-600
                             transition-colors"
                      :class="{ 'ring-2 ring-primary-500': selectedTags.includes(tag) }"
                      @click="toggleSuggestedTag(tag)"
                    >
                      {{ tag }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Footer -->
              <div class="flex items-center justify-end gap-3 p-5 border-t border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50">
                <button
                  class="px-4 py-2.5 text-sm font-medium rounded-xl
                         text-neutral-700 dark:text-neutral-300
                         hover:bg-neutral-200 dark:hover:bg-neutral-700
                         transition-colors"
                  @click="handleClose"
                >
                  Отмена
                </button>
                <button
                  class="px-5 py-2.5 text-sm font-medium rounded-xl
                         bg-primary-600 hover:bg-primary-700
                         text-white
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-colors"
                  :disabled="selectedTags.length === 0 || isSubmitting"
                  @click="handleSubmit"
                >
                  <span v-if="isSubmitting" class="flex items-center gap-2">
                    <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Применение...
                  </span>
                  <span v-else>
                    Применить теги
                  </span>
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
import { ref, watch, nextTick } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionRoot,
  TransitionChild,
} from '@headlessui/vue'

interface Props {
  isOpen: boolean
  selectedCount: number
  selectedIds: number[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: [tags: string[]]
}>()

const inputRef = ref<HTMLInputElement | null>(null)
const tagInput = ref('')
const selectedTags = ref<string[]>([])
const isSubmitting = ref(false)

const suggestedTags = [
  'Campaign 2025',
  'Marketing',
  'Product',
  'Social Media',
  'Press Release',
  'Internal',
  'Approved',
  'Archive',
]

// Focus input when modal opens
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen) {
    selectedTags.value = []
    tagInput.value = ''
    await nextTick()
    inputRef.value?.focus()
  }
})

function addTag() {
  const tag = tagInput.value.trim()
  if (tag && !selectedTags.value.includes(tag)) {
    selectedTags.value.push(tag)
    tagInput.value = ''
  }
}

function removeTag(index: number) {
  selectedTags.value.splice(index, 1)
}

function toggleSuggestedTag(tag: string) {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tag)
  }
}

function handleClose() {
  if (!isSubmitting.value) {
    emit('close')
  }
}

async function handleSubmit() {
  if (selectedTags.value.length === 0) return
  
  isSubmitting.value = true
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 800))
  
  isSubmitting.value = false
  emit('success', [...selectedTags.value])
}
</script>
