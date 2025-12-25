<template>
  <div class="p-6">
    <h1 class="text-xl font-semibold text-gray-900 mb-4">Архив уведомлений</h1>
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <NotificationCard
        v-for="n in items"
        :key="n.id"
        :notification="n"
        @read="markRead"
        @delete="deleteOne"
      />
      <NotificationEmpty v-if="items.length === 0" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'
import NotificationCard from '@/components/Notifications/NotificationCard.vue'
import NotificationEmpty from '@/components/Notifications/NotificationEmpty.vue'

const store = useNotificationStore()
const items = computed(() => store.centerNotifications)

const markRead = (id: number) => store.markCenterAsRead(id)
const deleteOne = (id: number) => store.deleteCenterNotification(id)

onMounted(() => {
  store.fetchCenterNotifications('ALL', 1)
})
</script>


