<template>
  <TransitionRoot as="template" :show="isOpen">
    <Dialog as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="div"
        enter="ease-out duration-200"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-150"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="div"
            enter="ease-out duration-200"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-150"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel
              class="w-full max-w-sm transform overflow-hidden rounded-xl bg-white 
                     shadow-2xl transition-all"
            >
              <!-- Header -->
              <div class="px-5 pt-5 pb-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 items-center justify-center rounded-full bg-amber-100">
                    <FolderPlusIcon class="h-5 w-5 text-amber-600" />
                  </div>
                  <DialogTitle class="text-lg font-semibold text-neutral-900">
                    Создать папку
                  </DialogTitle>
                </div>
              </div>

              <!-- Content -->
              <div class="px-5 pb-4">
                <label for="folder-name" class="block text-sm font-medium text-neutral-700 mb-1.5">
                  Название папки
                </label>
                <input
                  id="folder-name"
                  ref="inputRef"
                  v-model="folderName"
                  type="text"
                  class="w-full px-3 py-2.5 border border-neutral-300 rounded-lg text-sm
                         focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                         placeholder:text-neutral-400 transition-colors"
                  placeholder="Введите название..."
                  @keydown.enter="handleCreate"
                  @keydown.escape="handleClose"
                />
                <p v-if="error" class="mt-1.5 text-sm text-red-500">{{ error }}</p>
              </div>

              <!-- Footer -->
              <div class="flex justify-end gap-2 px-5 py-4 bg-neutral-50 border-t border-neutral-100">
                <button
                  type="button"
                  class="px-4 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300
                         rounded-lg hover:bg-neutral-50 transition-colors"
                  @click="handleClose"
                >
                  Отмена
                </button>
                <button
                  type="button"
                  class="px-4 py-2 text-sm font-medium text-white bg-primary-600
                         rounded-lg hover:bg-primary-700 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!folderName.trim() || isLoading"
                  @click="handleCreate"
                >
                  <span v-if="isLoading" class="flex items-center gap-2">
                    <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Создание...
                  </span>
                  <span v-else>Создать</span>
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
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import { FolderPlusIcon } from '@heroicons/vue/24/outline'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  create: [name: string]
}>()

const folderName = ref('')
const error = ref('')
const isLoading = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

// Focus input when modal opens
watch(() => props.isOpen, (open) => {
  if (open) {
    folderName.value = ''
    error.value = ''
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
})

function handleClose() {
  if (!isLoading.value) {
    emit('close')
  }
}

async function handleCreate() {
  const name = folderName.value.trim()
  
  if (!name) {
    error.value = 'Введите название папки'
    return
  }
  
  if (name.length > 100) {
    error.value = 'Название слишком длинное (макс. 100 символов)'
    return
  }
  
  isLoading.value = true
  error.value = ''
  
  try {
    emit('create', name)
    // Modal will be closed by parent after successful creation
  } finally {
    isLoading.value = false
  }
}
</script>

