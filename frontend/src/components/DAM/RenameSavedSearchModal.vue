<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="rename-search-modal-title"
      >
        <div class="absolute inset-0 bg-black/50" aria-hidden="true" @click="handleClose" />
        <div
          class="relative w-full max-w-md rounded-xl bg-white dark:bg-neutral-800 shadow-xl p-6"
          @keydown.escape="handleClose"
        >
          <h2 id="rename-search-modal-title" class="text-lg font-semibold text-neutral-900 dark:text-white">
            Переименовать поиск
          </h2>
          <form class="mt-4 space-y-4" @submit.prevent="handleSubmit">
            <input
              v-model="localName"
              type="text"
              class="block w-full rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 px-3 py-2 text-neutral-900 dark:text-white"
              maxlength="255"
              autocomplete="off"
              aria-label="Название"
            />
            <p v-if="error" class="text-sm text-red-600 dark:text-red-400" role="alert">{{ error }}</p>
            <div class="flex justify-end gap-2">
              <button
                type="button"
                class="px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg"
                @click="handleClose"
              >
                Отмена
              </button>
              <button
                type="submit"
                class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg disabled:opacity-50"
                :disabled="saving"
                aria-label="Сохранить"
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
import type { SavedSearch } from '@/services/savedSearchesService'

const props = defineProps<{
  isOpen: boolean
  item: SavedSearch | null
}>()

const emit = defineEmits<{
  close: []
  save: [id: number, name: string]
}>()

const localName = ref('')
const error = ref<string | null>(null)
const saving = ref(false)

watch(
  () => [props.isOpen, props.item] as const,
  ([open, item]) => {
    if (open && item) {
      localName.value = item.name
      error.value = null
    }
  }
)

function handleClose() {
  if (!saving.value) emit('close')
}

function handleSubmit() {
  const name = localName.value.trim()
  if (!name) {
    error.value = 'Введите название'
    return
  }
  if (!props.item) return
  error.value = null
  emit('save', props.item.id, name)
}

function setSaving(value: boolean) {
  saving.value = value
}
function setError(msg: string | null) {
  error.value = msg
}

defineExpose({ setSaving, setError })
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
