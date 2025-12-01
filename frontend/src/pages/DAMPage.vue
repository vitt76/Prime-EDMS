<template>
  <div class="dam-page">
    <GalleryView @open-upload="$emit('open-upload')" />
  </div>
</template>

<script setup lang="ts">
import GalleryView from '@/components/DAM/GalleryView.vue'

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

