<template>
  <div class="relative">
    <button
      type="button"
      class="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
      @click="toggle"
      :title="`Уведомления${unreadCount > 0 ? ` (${unreadCount})` : ''}`"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      <span
        v-if="unreadCount > 0"
        class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"
      />
      <span
        v-if="hasUrgent"
        class="absolute -top-0.5 -right-0.5 w-2 h-2 bg-red-600 rounded-full ring-2 ring-white"
        title="Есть срочные уведомления"
      />
    </button>

    <NotificationPopover v-if="isOpen" @close="isOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import NotificationPopover from './NotificationPopover.vue'

const isOpen = ref(false)
const notificationStore = useNotificationStore()
const { connect, disconnect } = useWebSocket()

const unreadCount = computed(() => notificationStore.centerUnreadCount)
const hasUrgent = computed(() => notificationStore.centerHasUrgent)

const toggle = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    notificationStore.fetchCenterNotifications('SENT', 1)
  }
}

onMounted(() => {
  notificationStore.getCenterUnreadCount()
  connect()
})

onUnmounted(() => {
  disconnect()
})
</script>


