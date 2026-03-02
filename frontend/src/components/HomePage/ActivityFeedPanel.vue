<template>
  <div class="activity-feed-panel bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 p-5">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold text-neutral-900 flex items-center gap-2">
        <span class="text-xl">⏱️</span> Активность
      </h2>
    </div>

    <!-- Loading State -->
    <div v-if="homeStore.isLoading && !homeStore.activityFeed.length" class="space-y-4">
      <div v-for="i in 3" :key="i" class="animate-pulse flex items-start gap-3">
        <div class="w-8 h-8 bg-neutral-200 rounded-full shrink-0"></div>
        <div class="flex-1 space-y-2">
          <div class="h-4 bg-neutral-200 rounded w-3/4"></div>
          <div class="h-3 bg-neutral-200 rounded w-1/4"></div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!homeStore.activityFeed.length" class="text-center py-8 text-neutral-500">
      <p>Нет недавней активности.</p>
    </div>

    <!-- Feed -->
    <div v-else class="relative">
      <div class="absolute top-0 bottom-0 left-4 w-px bg-neutral-100"></div>
      
      <div class="space-y-6">
        <div v-for="item in displayFeed" :key="item.id" class="relative flex gap-3">
          <!-- Icon -->
          <div class="w-8 h-8 rounded-full bg-primary-50 border-2 border-white flex items-center justify-center shrink-0 z-10 text-primary-600">
            <svg v-if="item.icon === 'upload'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
            <svg v-else-if="item.icon === 'download'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
            <svg v-else-if="item.icon === 'comment' || item.icon === 'chat'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          
          <!-- Content -->
          <div class="flex-1 pt-1.5 min-w-0">
            <p class="text-sm text-neutral-900 leading-tight">
              <span class="font-medium">{{ item.user }}</span>
              {{ item.action_text }}
              <span v-if="item.object_name" class="font-medium text-neutral-700">"{{ item.object_name }}"</span>
            </p>
            <div class="text-xs text-neutral-500 mt-1">
              {{ formatTimeAgo(item.timestamp) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useHomeStore } from '@/stores/homeStore'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

const homeStore = useHomeStore()

const displayFeed = computed(() => {
  return homeStore.activityFeed.slice(0, 10)
})

function formatTimeAgo(dateString: string) {
  try {
    const date = new Date(dateString)
    return formatDistanceToNow(date, { addSuffix: true, locale: ru })
  } catch {
    return dateString
  }
}
</script>