<template>
  <NuxtLayout>
    <NuxtPage :transition="pageTransition" />
  </NuxtLayout>
</template>

<script setup lang="ts">
const pageTransition = {
  name: 'page',
  mode: 'out-in'
}
</script>

<style>
/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease-out;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Layout transition */
.layout-enter-active,
.layout-leave-active {
  transition: all 0.3s ease-out;
}

.layout-enter-from,
.layout-leave-to {
  opacity: 0;
}
</style>
