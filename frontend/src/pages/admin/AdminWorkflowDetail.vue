<template>
  <div class="admin-workflow-detail space-y-6">
    <!-- Back Link -->
    <router-link
      to="/admin/workflows"
      class="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Назад к списку процессов
    </router-link>

    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <p class="text-center text-gray-500">
        Редактор рабочего процесса (ID: {{ $route.params.id }})
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

