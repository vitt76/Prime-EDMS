<template>
  <div id="my-inbox-section" class="bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 overflow-hidden flex flex-col">
    <div class="px-5 py-4 border-b border-neutral-100 flex justify-between items-center">
      <h2 class="text-lg font-semibold text-neutral-900 flex items-center gap-2">
        <span class="text-xl">📬</span> Входящие
        <span v-if="unreadCount > 0" class="bg-error text-white text-xs font-bold px-2 py-0.5 rounded-full">
          {{ unreadCount }}
        </span>
      </h2>
      <button 
        @click="goToNotifications"
        class="text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        Показать все
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="notificationStore.centerIsLoading" class="p-5 space-y-4">
      <div v-for="i in 3" :key="i" class="animate-pulse flex gap-3">
        <div class="w-8 h-8 bg-neutral-200 rounded-full"></div>
        <div class="flex-1 space-y-2">
          <div class="h-4 bg-neutral-200 rounded w-1/4"></div>
          <div class="h-3 bg-neutral-200 rounded w-3/4"></div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!displayNotifications.length" class="p-8 text-center text-neutral-500">
      <p>У вас нет новых уведомлений.</p>
    </div>

    <!-- List -->
    <div v-else class="divide-y divide-neutral-50">
      <NotificationCard 
        v-for="notification in displayNotifications" 
        :key="notification.id"
        :notification="notification"
        @read="markAsRead"
        @delete="deleteNotification"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notificationStore'
import NotificationCard from '@/components/Notifications/NotificationCard.vue'

const router = useRouter()
const notificationStore = useNotificationStore()

// We only show the latest 5-6 notifications in the inbox widget
const displayNotifications = computed(() => {
  return notificationStore.centerNotifications.slice(0, 6)
})

const unreadCount = computed(() => notificationStore.centerUnreadCount)

onMounted(() => {
  if (notificationStore.centerNotifications.length === 0) {
    notificationStore.fetchCenterNotifications('SENT')
  }
})

function goToNotifications() {
  // Try to use a router push or open the popover
  // We'll route to the notification archive page if it exists
  router.push({ name: 'notifications-archive' })
}

function markAsRead(id: number) {
  notificationStore.markCenterNotificationAsRead(id)
}

function deleteNotification(id: number) {
  notificationStore.deleteCenterNotification(id)
}
</script>