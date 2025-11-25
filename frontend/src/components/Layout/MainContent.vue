<template>
  <main
    :class="[
      'transition-all duration-300 ease-in-out',
      sidebarExpanded ? 'ml-70' : 'ml-16',
      'mt-16 min-h-[calc(100vh-4rem)]'
    ]"
  >
    <div class="p-4 md:p-6 lg:p-8">
      <slot />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUIStore } from '@/stores/uiStore'

const uiStore = useUIStore()
const sidebarExpanded = computed(() => uiStore.sidebarExpanded)
</script>

<style scoped>
.ml-70 {
  margin-left: 280px;
}
</style>

