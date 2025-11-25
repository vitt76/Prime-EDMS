<template>
  <Transition
    enter-active-class="transition ease-out duration-200"
    enter-from-class="opacity-0 translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition ease-in duration-150"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 translate-y-2"
  >
    <div
      v-if="selectedCount > 0"
      class="bulk-actions fixed bottom-0 left-0 right-0 bg-neutral-0 dark:bg-neutral-0 border-t border-neutral-300 dark:border-neutral-300 shadow-lg z-40"
    >
      <div class="max-w-7xl mx-auto px-4 py-3">
        <div class="flex items-center justify-between">
          <!-- Selection Counter -->
          <div class="flex items-center gap-4">
            <span class="text-sm font-medium text-neutral-900 dark:text-neutral-900">
              Выбрано: <span class="font-bold">{{ selectedCount }}</span>
            </span>
            <button
              class="text-sm text-neutral-600 dark:text-neutral-600 hover:text-neutral-900 dark:hover:text-neutral-900 transition-colors"
              @click="$emit('clear-selection')"
            >
              Снять выделение
            </button>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              @click="$emit('tag')"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                />
              </svg>
              Теги
            </Button>
            <Button
              variant="outline"
              size="sm"
              @click="$emit('move')"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 10h18M7 15l1-1m8 0l1-1m-9 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              Переместить
            </Button>
            <Button
              variant="outline"
              size="sm"
              @click="$emit('download')"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Скачать
            </Button>
            <Button
              variant="outline"
              size="sm"
              @click="$emit('share')"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.552 3.546a2 2 0 002.938-2.187l.546-2.59A4.998 4.998 0 0017 12c0-.482-.114-.938-.316-1.342m0 2.684L12.448 8.454a2 2 0 00-2.938-2.187l-.546 2.59A4.998 4.998 0 007 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684"
                />
              </svg>
              Поделиться
            </Button>
            <Button
              variant="danger"
              size="sm"
              @click="$emit('delete')"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Удалить
            </Button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import Button from '@/components/Common/Button.vue'

interface Props {
  selectedCount: number
}

defineProps<Props>()

defineEmits<{
  tag: []
  move: []
  download: []
  share: []
  delete: []
  'clear-selection': []
}>()
</script>

<style scoped>
.bulk-actions {
  /* Fixed at bottom with proper spacing */
  margin-left: var(--sidebar-width, 0);
  transition: margin-left 0.3s ease;
}

@media (max-width: 1024px) {
  .bulk-actions {
    margin-left: 0;
  }
}
</style>

