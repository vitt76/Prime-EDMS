<template>
  <div :style="{ aspectRatio: `${width}/${height}` }" class="relative">
    <NuxtImg
      :src="src"
      :alt="alt"
      :width="width"
      :height="height"
      :loading="loading"
      :format="format"
      :quality="quality"
      :class="imgClass"
      class="absolute inset-0 h-full w-full object-cover"
      @load="onLoad"
      @error="onError"
    />

    <div
      v-if="!loaded && showPlaceholder"
      class="absolute inset-0 animate-pulse bg-gradient-to-br from-neutral-100 to-neutral-200"
    ></div>

    <div
      v-if="error"
      class="absolute inset-0 flex items-center justify-center bg-neutral-100"
    >
      <PhotoIcon class="h-12 w-12 text-neutral-300" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { PhotoIcon } from '@heroicons/vue/24/outline'

const props = withDefaults(
  defineProps<{
    src: string
    alt: string
    width: number
    height: number
    loading?: 'lazy' | 'eager'
    format?: 'webp' | 'avif' | 'jpg'
    quality?: number
    imgClass?: string
    showPlaceholder?: boolean
  }>(),
  {
    loading: 'lazy',
    format: 'webp',
    quality: 80,
    showPlaceholder: true
  }
)

const loaded = ref(false)
const error = ref(false)

const onLoad = () => {
  loaded.value = true
}

const onError = () => {
  error.value = true
}
</script>
