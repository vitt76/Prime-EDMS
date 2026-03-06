<template>
  <div class="asset-thumbnail w-full h-full">
    <img
      v-if="resolvedSrc && !imageError && loaded"
      :src="resolvedSrc"
      :srcset="srcset || undefined"
      :sizes="sizes || undefined"
      :alt="alt"
      loading="lazy"
      :class="objectFitClass"
      class="w-full h-full object-center transition-opacity duration-300"
      @error="handleError"
      @load="handleLoad"
    />
    <img
      v-else-if="resolvedSrc && !imageError && !loaded"
      :src="resolvedSrc"
      :alt="alt"
      loading="lazy"
      :class="objectFitClass"
      class="w-full h-full object-center opacity-0"
      @error="handleError"
      @load="handleLoad"
    />
    <div
      v-else-if="!loaded && !imageError"
      class="w-full h-full flex items-center justify-center bg-gradient-to-br from-neutral-100 to-neutral-200 dark:from-neutral-700 dark:to-neutral-800 animate-pulse"
    >
      <div class="w-12 h-12 rounded-full bg-neutral-300 dark:bg-neutral-600" />
    </div>
    <div
      v-else
      class="w-full h-full flex items-center justify-center bg-gradient-to-br from-neutral-100 to-neutral-200 dark:from-neutral-700 dark:to-neutral-800"
    >
      <svg
        class="w-12 h-12 text-neutral-400 dark:text-neutral-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AssetThumbnail: lazy-loaded image with placeholder and error state.
 * Uses native loading="lazy", optional srcset/sizes, and solid/gradient placeholder.
 */

import { ref, watch, onBeforeUnmount } from 'vue'
import { apiService } from '@/services/apiService'

interface Props {
  src: string | null | undefined
  alt: string
  objectFitClass?: string
  srcset?: string
  sizes?: string
  placeholder?: 'solid' | string
}

const props = withDefaults(defineProps<Props>(), {
  objectFitClass: 'object-cover',
  placeholder: 'solid'
})

const loaded = ref(false)
const imageError = ref(false)
const resolvedSrc = ref<string | null>(null)
let blobObjectUrl: string | null = null

function revokeBlobUrl() {
  if (blobObjectUrl) {
    URL.revokeObjectURL(blobObjectUrl)
    blobObjectUrl = null
  }
}

watch(
  () => props.src,
  async (newSrc) => {
    loaded.value = false
    imageError.value = false
    revokeBlobUrl()
    resolvedSrc.value = null

    if (!newSrc) {
      imageError.value = true
      return
    }

    if (newSrc.includes('/api/v4/')) {
      try {
        const response: any = await apiService.get(newSrc, {
          responseType: 'blob',
          headers: { Accept: '*/*' } as any
        })
        const blob = response instanceof Blob ? response : (response?.data as Blob)
        if (blob && blob.size > 0) {
          blobObjectUrl = URL.createObjectURL(blob)
          resolvedSrc.value = blobObjectUrl
          return
        }
      } catch (e) {
        console.warn('AssetThumbnail: failed to fetch blob', e)
        imageError.value = true
        return
      }
    }

    // fallback for non-protected or absolute URLs
    resolvedSrc.value = newSrc
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  revokeBlobUrl()
})

function handleLoad() {
  loaded.value = true
}

function handleError() {
  imageError.value = true
}
</script>

<style scoped>
.asset-thumbnail {
  min-height: 0;
}
</style>
