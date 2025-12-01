<template>
  <div class="dam-page">
    <GalleryView @open-upload="$emit('open-upload')" />
    
    <!-- API Debug Panel (DEV only) - lazy loaded -->
    <Suspense v-if="isDev">
      <template #default>
        <ApiDebugPanel />
      </template>
      <template #fallback>
        <div></div>
      </template>
    </Suspense>
  </div>
</template>

<script setup lang="ts">
import { ref, defineAsyncComponent } from 'vue'
import GalleryView from '@/components/DAM/GalleryView.vue'

// Lazy load debug panel to avoid blocking main page
const ApiDebugPanel = defineAsyncComponent(() => 
  import('@/components/Debug/ApiDebugPanel.vue')
)

const isDev = ref(import.meta.env.DEV)

defineEmits<{
  'open-upload': []
}>()
</script>

<style scoped>
.dam-page {
  width: 100%;
  min-height: 100vh;
}
</style>

