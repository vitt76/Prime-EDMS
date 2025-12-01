<template>
  <div class="min-h-screen bg-neutral-50 dark:bg-neutral-50">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-4xl font-semibold mb-4">DAM System</h1>
      <p class="text-lg text-neutral-600 dark:text-neutral-600 mb-8">
        Digital Asset Management System Frontend
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <h2 class="text-xl font-semibold mb-2">Components</h2>
          <p class="text-sm text-neutral-600 dark:text-neutral-600">
            Reusable UI components built with Vue 3 and Tailwind CSS
          </p>
        </Card>

        <Card>
          <h2 class="text-xl font-semibold mb-2">State Management</h2>
          <p class="text-sm text-neutral-600 dark:text-neutral-600">
            Pinia stores for global state management
          </p>
        </Card>

        <Card>
          <h2 class="text-xl font-semibold mb-2">API Integration</h2>
          <p class="text-sm text-neutral-600 dark:text-neutral-600">
            Axios-based API client with interceptors
          </p>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
</script>


