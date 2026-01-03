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

      <div class="ml-auto flex items-center gap-2">
        <select
          class="text-xs px-2 py-1 rounded-md border border-gray-200 bg-white text-gray-700"
          :value="category"
          @change="setCategory(($event.target as HTMLSelectElement).value as any)"
          title="Категория"
        >
          <option value="all">Все категории</option>
          <option value="uploads">Загрузка</option>
          <option value="processing">Обработка</option>
          <option value="views">Просмотры</option>
          <option value="downloads">Скачивания</option>
          <option value="lifecycle">Жизненный цикл</option>
        </select>

        <label v-if="isAdmin" class="inline-flex items-center gap-1 text-xs text-gray-600 select-none">
          <input
            type="checkbox"
            class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            :checked="scope === 'all'"
            @change="toggleScope"
          />
          Системные
        </label>
      </div>
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
import { storeToRefs } from 'pinia'
import { useNotificationStore } from '@/stores/notificationStore'
import { useAuthStore } from '@/stores/authStore'
import NotificationCard from './NotificationCard.vue'
import NotificationEmpty from './NotificationEmpty.vue'

defineEmits<{ close: [] }>()

const store = useNotificationStore()
const authStore = useAuthStore()

// Use storeToRefs() to avoid ambiguity between Pinia-unwrapped values and refs.
const {
  centerFilter: filter,
  centerCategory: category,
  centerScope: scope,
  centerUnreadCount: unreadCount,
  centerFilteredNotifications: items
} = storeToRefs(store)

const setFilter = (value: 'all' | 'unread' | 'important') => store.setCenterFilter(value)
const setCategory = (value: 'all' | 'uploads' | 'processing' | 'views' | 'downloads' | 'lifecycle') =>
  store.setCenterCategory(value, 'SENT')
const markRead = (id: number) => store.markCenterAsRead(id)
const markAll = () => store.markAllCenterAsRead()
const deleteOne = (id: number) => store.deleteCenterNotification(id)

const isAdmin = computed(() => {
  const user = authStore.user as any
  const groups = (user?.groups || []) as Array<{ name: string }>
  return !!(user?.is_staff || user?.is_superuser || groups.some((g) => (g?.name || '').toLowerCase() === 'admin'))
})

const toggleScope = () => {
  // Popover is the "recent" view, keep SENT state.
  store.setCenterScope(scope.value === 'all' ? 'dam' : 'all', 'SENT')
}

// NOTE: Do not fetch here.
// The popover is rendered only when the bell is opened, and the bell already
// triggers a fetch. Keeping a second fetch here causes duplicate requests.
</script>


