<template>
  <div
    class="absolute right-0 mt-2 w-[420px] max-w-[95vw] bg-white rounded-xl shadow-lg border border-gray-200 z-50 overflow-hidden"
  >
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
      <div class="font-semibold text-gray-900">Уведомления</div>
      <div class="flex items-center gap-2">
        <button
          v-if="unreadCount > 0"
          class="text-xs text-indigo-600 hover:text-indigo-800"
          @click="markAll"
        >
          Отметить все
        </button>
        <button class="text-gray-500 hover:text-gray-700" @click="$emit('close')">
          ✕
        </button>
      </div>
    </div>

    <div class="flex gap-2 px-4 py-2 border-b border-gray-100">
      <button
        class="text-xs px-2 py-1 rounded-md"
        :class="filter === 'all' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50'"
        @click="setFilter('all')"
      >
        Все
      </button>
      <button
        class="text-xs px-2 py-1 rounded-md"
        :class="filter === 'unread' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50'"
        @click="setFilter('unread')"
      >
        Непрочитанные
      </button>
      <button
        class="text-xs px-2 py-1 rounded-md"
        :class="filter === 'important' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50'"
        @click="setFilter('important')"
      >
        Важные
      </button>
    </div>

    <div class="max-h-[420px] overflow-auto">
      <NotificationEmpty v-if="items.length === 0" />
      <NotificationCard
        v-for="n in items"
        :key="n.id"
        :notification="n"
        @read="markRead"
        @delete="deleteOne"
      />
    </div>

    <div class="flex items-center justify-between px-4 py-3 border-t border-gray-100">
      <router-link to="/notifications/archive" class="text-sm text-indigo-600 hover:text-indigo-800">
        Все уведомления →
      </router-link>
      <router-link to="/notifications/settings" class="text-sm text-gray-600 hover:text-gray-800">
        Настройки
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'
import NotificationCard from './NotificationCard.vue'
import NotificationEmpty from './NotificationEmpty.vue'

defineEmits<{ close: [] }>()

const store = useNotificationStore()

const filter = computed(() => store.centerFilter)
const unreadCount = computed(() => store.centerUnreadCount)
const items = computed(() => store.centerFilteredNotifications)

const setFilter = (value: 'all' | 'unread' | 'important') => store.setCenterFilter(value)
const markRead = (id: number) => store.markCenterAsRead(id)
const markAll = () => store.markAllCenterAsRead()
const deleteOne = (id: number) => store.deleteCenterNotification(id)
</script>


