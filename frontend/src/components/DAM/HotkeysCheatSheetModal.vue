<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="hotkeys-title"
      >
        <div
          class="absolute inset-0 bg-black/50"
          aria-hidden="true"
          @click="emit('close')"
        />
        <div
          class="relative w-full max-w-md rounded-xl bg-white dark:bg-neutral-800 shadow-xl p-6"
          @keydown.escape="emit('close')"
        >
          <h2
            id="hotkeys-title"
            class="text-lg font-semibold text-neutral-900 dark:text-white mb-4"
          >
            Горячие клавиши
          </h2>
          <table class="w-full text-sm text-left text-neutral-700 dark:text-neutral-300">
            <thead>
              <tr class="border-b border-neutral-200 dark:border-neutral-600">
                <th class="py-2 pr-4 font-medium">Клавиша</th>
                <th class="py-2">Действие</th>
              </tr>
            </thead>
            <tbody>
              <tr class="border-b border-neutral-100 dark:border-neutral-700">
                <td class="py-2 pr-4"><kbd class="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-700 font-mono">F</kbd></td>
                <td class="py-2">Добавить/убрать из избранного</td>
              </tr>
              <tr class="border-b border-neutral-100 dark:border-neutral-700">
                <td class="py-2 pr-4"><kbd class="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-700 font-mono">Space</kbd></td>
                <td class="py-2">Превью выделенного</td>
              </tr>
              <tr class="border-b border-neutral-100 dark:border-neutral-700">
                <td class="py-2 pr-4"><kbd class="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-700 font-mono">Delete</kbd> / <kbd class="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-700 font-mono">Backspace</kbd></td>
                <td class="py-2">В корзину</td>
              </tr>
              <tr class="border-b border-neutral-100 dark:border-neutral-700">
                <td class="py-2 pr-4"><kbd class="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-700 font-mono">Esc</kbd></td>
                <td class="py-2">Снять выделение / закрыть модалку</td>
              </tr>
              <tr class="border-b border-neutral-100 dark:border-neutral-700">
                <td class="py-2 pr-4"><kbd class="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-700 font-mono">Ctrl</kbd>+<kbd class="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-700 font-mono">A</kbd></td>
                <td class="py-2">Выделить все</td>
              </tr>
              <tr class="border-b border-neutral-100 dark:border-neutral-700">
                <td class="py-2 pr-4"><kbd class="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-700 font-mono">?</kbd></td>
                <td class="py-2">Эта подсказка</td>
              </tr>
            </tbody>
          </table>
          <div class="mt-4 flex justify-end">
            <button
              type="button"
              class="px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400"
              @click="emit('close')"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  close: []
}>()
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
