<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="save-search-modal-title"
        aria-describedby="save-search-modal-desc"
      >
        <div
          class="absolute inset-0 bg-black/50"
          aria-hidden="true"
          @click="handleClose"
        />
        <div
          class="relative w-full max-w-md rounded-xl bg-white dark:bg-neutral-800 shadow-xl p-6"
          @keydown.escape="handleClose"
        >
          <h2
            id="save-search-modal-title"
            class="text-lg font-semibold text-neutral-900 dark:text-white"
          >
            Сохранить поиск
          </h2>
          <p
            id="save-search-modal-desc"
            class="mt-1 text-sm text-neutral-500 dark:text-neutral-400"
          >
            Текущий запрос и фильтры будут сохранены под выбранным именем.
          </p>
          <form class="mt-4 space-y-4" @submit.prevent="handleSubmit">
            <div>
              <label for="save-search-name" class="block text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Название
              </label>
              <input
                id="save-search-name"
                v-model="localName"
                type="text"
                class="mt-1 block w-full rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 px-3 py-2 text-neutral-900 dark:text-white placeholder-neutral-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                placeholder="Например: Альбомные изображения"
                maxlength="255"
                autocomplete="off"
                aria-invalid="!!validationError"
                aria-describedby="save-search-error"
                @input="validationError = null"
              />
              <p
                v-if="validationError || props.backendError"
                id="save-search-error"
                class="mt-1.5 text-sm text-red-600 dark:text-red-400"
                role="alert"
              >
                {{ validationError || props.backendError }}
              </p>
            </div>
            <div class="flex justify-end gap-2">
              <button
                type="button"
                class="px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
                @click="handleClose"
              >
                Отмена
              </button>
              <button
                type="submit"
                class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="saving"
                aria-label="Сохранить поиск"
              >
                {{ saving ? 'Сохранение…' : 'Сохранить' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  isOpen: boolean
  /** Backend validation error (e.g. max saved searches limit) */
  backendError?: string | null
}>()

const emit = defineEmits<{
  close: []
  save: [name: string]
}>()

const localName = ref('')
const validationError = ref<string | null>(null)
const saving = ref(false)

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      localName.value = ''
      validationError.value = null
    }
  }
)

function handleClose() {
  if (saving.value) return
  emit('close')
}

function handleSubmit() {
  const name = localName.value.trim()
  if (!name) {
    validationError.value = 'Введите название'
    return
  }
  validationError.value = null
  emit('save', name)
}

function setSaving(value: boolean) {
  saving.value = value
}

function setValidationError(message: string | null) {
  validationError.value = message
}

defineExpose({
  setSaving,
  setValidationError
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
