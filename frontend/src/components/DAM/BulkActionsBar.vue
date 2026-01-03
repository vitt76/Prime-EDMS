<template>
  <Transition
    enter-active-class="transform transition-all duration-300 ease-out"
    enter-from-class="translate-y-full opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transform transition-all duration-200 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-full opacity-0"
  >
    <div
      v-if="selectedCount > 0"
      class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[1000]
             bg-neutral-900/90 backdrop-blur-xl 
             rounded-2xl shadow-2xl shadow-black/30
             border border-neutral-700/50
             px-6 py-4 flex items-center gap-6"
    >
      <!-- Selection Info -->
      <div class="flex items-center gap-3 pr-6 border-r border-neutral-700">
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary-500/20 text-primary-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <p class="text-white font-semibold text-sm">
            {{ selectedCount }} {{ selectedLabel }}
          </p>
          <p class="text-neutral-400 text-xs">
            Выбрано
          </p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <!-- Download -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-neutral-800 hover:bg-neutral-700 
                 text-white text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="$emit('download')"
          title="Скачать выбранные"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span class="hidden sm:inline">Скачать</span>
        </button>

      <!-- Share -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-neutral-800 hover:bg-neutral-700 
                 text-white text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="$emit('share')"
          title="Поделиться"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <span class="hidden sm:inline">Поделиться</span>
        </button>

        <!-- Delete -->
        <button
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl
                 bg-red-500/20 hover:bg-red-500/30 
                 text-red-400 hover:text-red-300 text-sm font-medium
                 transition-all duration-200 hover:scale-105"
          @click="$emit('delete')"
          title="Удалить"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span class="hidden sm:inline">Удалить</span>
        </button>
      </div>

      <!-- Clear Selection -->
      <button
        class="ml-2 p-2.5 rounded-xl
               bg-neutral-800 hover:bg-neutral-700 
               text-neutral-400 hover:text-white
               transition-all duration-200"
        @click="$emit('clear')"
        title="Снять выделение"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAssetStore } from '@/stores/assetStore'

const assetStore = useAssetStore()

defineEmits<{
  download: []
  share: []
  delete: []
  clear: []
}>()

const selectedCount = computed(() => assetStore.selectedAssets.size)

const selectedLabel = computed(() => {
  const count = selectedCount.value
  if (count === 1) return 'актив'
  if (count >= 2 && count <= 4) return 'актива'
  return 'активов'
})
</script>

