<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-4 gap-3">
      <h1 class="text-xl font-semibold text-gray-900">Архив уведомлений</h1>
      <div class="flex items-center gap-2">
        <select
          class="text-sm px-3 py-2 rounded-lg border border-gray-200 bg-white text-gray-700"
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

        <label v-if="isAdmin" class="inline-flex items-center gap-2 text-sm text-gray-600 select-none">
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
import { useAuthStore } from '@/stores/authStore'
import NotificationCard from '@/components/Notifications/NotificationCard.vue'
import NotificationEmpty from '@/components/Notifications/NotificationEmpty.vue'

const store = useNotificationStore()
const authStore = useAuthStore()
const items = computed(() => store.centerFilteredNotifications)
const category = computed(() => store.centerCategory)
const scope = computed(() => store.centerScope)

const setCategory = (value: 'all' | 'uploads' | 'processing' | 'views' | 'downloads' | 'lifecycle') =>
  store.setCenterCategory(value)

const isAdmin = computed(() => {
  const user = authStore.user as any
  const groups = (user?.groups || []) as Array<{ name: string }>
  return !!(user?.is_staff || user?.is_superuser || groups.some((g) => (g?.name || '').toLowerCase() === 'admin'))
})

const toggleScope = () => {
  store.setCenterScope(scope.value === 'all' ? 'dam' : 'all')
}

const markRead = (id: number) => store.markCenterAsRead(id)
const deleteOne = (id: number) => store.deleteCenterNotification(id)

onMounted(() => {
  // Archive should show all items by default (filter tabs are only in popover).
  store.setCenterFilter('all')
  store.fetchCenterNotifications('ALL', 1)
})
</script>


