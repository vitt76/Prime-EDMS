<template>
  <div class="ai-insights-card bg-primary-50 dark:bg-primary-900/20 rounded-lg shadow-sm border border-primary-100 p-5 relative overflow-hidden group">
    <!-- Decorative background element -->
    <div class="absolute -right-6 -top-6 w-24 h-24 bg-primary-100 dark:bg-primary-800/30 rounded-full opacity-50 group-hover:scale-110 transition-transform"></div>
    
    <div class="relative z-10">
      <h2 class="text-lg font-semibold text-primary-900 flex items-center gap-2 mb-2">
        <span class="text-xl">💡</span> AI Инсайты
      </h2>

      <!-- Loading State -->
      <div v-if="homeStore.isLoading && !homeStore.insights.length" class="animate-pulse space-y-2 mt-4">
        <div class="h-4 bg-primary-200 rounded w-3/4"></div>
        <div class="h-8 bg-primary-200 rounded w-1/2 mt-4"></div>
      </div>

      <!-- Content -->
      <div v-else-if="homeStore.insights.length" class="mt-2">
        <div v-for="(insight, index) in homeStore.insights" :key="index" class="mb-4 last:mb-0">
          <p class="text-primary-800 font-medium mb-3">
            {{ insight.emoji }} {{ insight.message }}
          </p>
          <button 
            @click="handleAction(insight)"
            class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors"
          >
            {{ insight.cta_label }}
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="mt-2 text-sm text-primary-700">
        На сегодня нет новых рекомендаций. Ваша медиатека в отличном состоянии! ✨
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHomeStore, type AIInsight } from '@/stores/homeStore'
import { useRouter } from 'vue-router'

const homeStore = useHomeStore()
const router = useRouter()

function handleAction(insight: AIInsight) {
  // Map actions based on insight type
  if (insight.type === 'auto_tag_missing') {
    router.push({ name: 'dam', query: { status: 'untagged' } })
    return
  }

  if (insight.type === 'ai_failed') {
    router.push({ name: 'dam', query: { status: 'failed' } })
  }
}
</script>