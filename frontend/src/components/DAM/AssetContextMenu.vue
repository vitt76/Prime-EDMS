<template>
  <Teleport to="body">
    <div
      v-if="open && asset"
      class="fixed z-[1000] min-w-[180px] py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg"
      :style="{ left: `${x}px`, top: `${y}px` }"
      role="menu"
      aria-label="Действия с активом"
    >
      <button
        type="button"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
        role="menuitem"
        @click="onOpen"
      >
        <span>Открыть</span>
      </button>
      <button
        type="button"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
        role="menuitem"
        @click="onDownload"
      >
        <span>Скачать</span>
      </button>
      <button
        type="button"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
        role="menuitem"
        @click="onShare"
      >
        <span>Поделиться</span>
      </button>
      <button
        type="button"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
        role="menuitem"
        @click="onEditMetadata"
      >
        <span>Редактировать метаданные</span>
      </button>
      <button
        type="button"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
        role="menuitem"
        @click="onAiTag"
      >
        <span>Тегировать с AI</span>
      </button>
      <div class="border-t border-gray-200 dark:border-gray-700 my-1" />
      <button
        type="button"
        class="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
        role="menuitem"
        @click="onDelete"
      >
        <span>Удалить</span>
      </button>
    </div>
    <div
      v-if="open"
      class="fixed inset-0 z-[999]"
      aria-hidden="true"
      @click="onClose"
    />
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import type { Asset } from '@/types/api'

interface Props {
  open: boolean
  x: number
  y: number
  asset: Asset | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  open: [asset: Asset]
  download: [asset: Asset]
  share: [asset: Asset]
  'edit-metadata': [asset: Asset]
  'ai-tag': [asset: Asset]
  delete: [asset: Asset]
}>()

function onOpen() {
  if (props.asset) emit('open', props.asset)
  emit('close')
}

function onDownload() {
  if (props.asset) emit('download', props.asset)
  emit('close')
}

function onShare() {
  if (props.asset) emit('share', props.asset)
  emit('close')
}

function onEditMetadata() {
  if (props.asset) emit('edit-metadata', props.asset)
  emit('close')
}

function onAiTag() {
  if (props.asset) emit('ai-tag', props.asset)
  emit('close')
}

function onDelete() {
  if (props.asset) emit('delete', props.asset)
  emit('close')
}

function onClose() {
  emit('close')
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    onClose()
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>
