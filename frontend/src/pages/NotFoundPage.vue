<template>
  <div class="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-50">
    <div class="text-center">
      <h1 class="text-6xl font-bold mb-4">404</h1>
      <p class="text-xl text-neutral-600 dark:text-neutral-600 mb-8">Page not found</p>
      <Button variant="primary" @click="$router.push('/')">Go Home</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from '@/components/Common/Button.vue'
</script>


