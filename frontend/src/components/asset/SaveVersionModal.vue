<template>
  <TransitionRoot as="div" :show="isOpen">
    <Dialog as="div" class="relative z-50" @close="handleCancel">
      <TransitionChild
        as="div"
        enter="ease-out duration-200"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-150"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm" />
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
              class="w-full max-w-lg transform overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-neutral-900"
            >
              <div class="px-6 py-5 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between">
                <DialogTitle class="text-lg font-semibold text-neutral-900 dark:text-white">
                  Сохранить новую версию
                </DialogTitle>
                <button
                  class="p-2 rounded-lg text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100 dark:hover:text-white dark:hover:bg-neutral-800 transition-colors"
                  @click="handleCancel"
                  :disabled="isSubmitting"
                >
                  <XMarkIcon class="w-5 h-5" />
                </button>
              </div>

              <div class="px-6 py-5 space-y-4">
                <div>
                  <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-200 mb-2">
                    Формат файла
                  </label>
                  <select
                    v-model="localFormat"
                    class="w-full rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    :disabled="isSubmitting"
                  >
                    <option value="original">Оригинал</option>
                    <option value="jpg">JPG</option>
                    <option value="png">PNG</option>
                    <option value="webp">WebP</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-200 mb-2">
                    Комментарий
                  </label>
                  <textarea
                    v-model="localComment"
                    rows="3"
                    class="w-full rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Опишите изменения (необязательно)"
                    :disabled="isSubmitting"
                  />
                </div>

                <p v-if="error || props.errorMessage" class="text-sm text-red-500">
                  {{ props.errorMessage || error }}
                </p>
              </div>

              <div class="px-6 py-4 bg-neutral-50 dark:bg-neutral-900/60 border-t border-neutral-200 dark:border-neutral-800 flex items-center justify-end gap-2">
                <button
                  class="px-4 py-2 text-sm font-medium text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
                  @click="handleCancel"
                  :disabled="isSubmitting"
                >
                  Отмена
                </button>
                <button
                  class="px-4 py-2 text-sm font-semibold text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-60 flex items-center gap-2"
                  :disabled="isSubmitting"
                  @click="handleSave"
                >
                  <svg
                    v-if="isSubmitting"
                    class="animate-spin h-4 w-4 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span>{{ isSubmitting ? 'Сохранение...' : 'Сохранить версию' }}</span>
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
import { ref, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

interface Props {
  isOpen: boolean
  defaultFormat?: string
  errorMessage?: string | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  save: [format: string, comment: string]
}>()

const localFormat = ref<string>(props.defaultFormat || 'original')
const localComment = ref<string>('')
const isSubmitting = ref(false)
const error = ref<string | null>(null)

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      localFormat.value = props.defaultFormat || 'original'
      error.value = null
      isSubmitting.value = false
    }
  }
)

function handleCancel() {
  if (isSubmitting.value) return
  emit('close')
}

async function handleSave() {
  if (isSubmitting.value) return
  error.value = null
  isSubmitting.value = true
  try {
    emit('save', localFormat.value, localComment.value.trim())
  } catch (e: any) {
    error.value = e?.message || 'Не удалось сохранить'
  } finally {
    isSubmitting.value = false
  }
}
</script>

