<template>
  <picture>
    <!-- WebP source with fallback -->
    <source
      v-if="webpUrl"
      :srcset="webpUrl"
      type="image/webp"
    />
    <!-- Original image as fallback -->
    <img
      :src="src"
      :alt="alt"
      :loading="loading"
      :class="imageClasses"
      @error="handleError"
      @load="handleLoad"
    />
  </picture>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  src: string
  alt: string
  loading?: 'lazy' | 'eager'
  webpUrl?: string
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: 'lazy',
  webpUrl: undefined
})

const imageError = ref(false)
const imageLoaded = ref(false)

const imageClasses = computed(() => {
  return [
    props.class,
    imageLoaded.value ? 'opacity-100' : 'opacity-0',
    'transition-opacity duration-300'
  ].filter(Boolean).join(' ')
})

function handleError() {
  imageError.value = true
}

function handleLoad() {
  imageLoaded.value = true
}

// Generate WebP URL from original URL if not provided
const webpUrl = computed(() => {
  if (props.webpUrl) return props.webpUrl
  
  // Try to generate WebP URL by replacing extension
  if (props.src && !imageError.value) {
    const url = new URL(props.src, window.location.origin)
    const pathname = url.pathname
    const webpPath = pathname.replace(/\.(jpg|jpeg|png)$/i, '.webp')
    return webpPath !== pathname ? `${url.origin}${webpPath}` : undefined
  }
  return undefined
})
</script>





