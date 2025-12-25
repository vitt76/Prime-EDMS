<template>
  <div class="p-6">
    <h1 class="text-xl font-semibold text-gray-900 mb-4">Настройки уведомлений</h1>
    <div class="bg-white rounded-xl border border-gray-200 p-4 max-w-xl">
      <div class="flex items-center justify-between py-2">
        <div>
          <div class="font-medium text-gray-900">Уведомления</div>
          <div class="text-sm text-gray-500">Включить/выключить получение уведомлений</div>
        </div>
        <input type="checkbox" v-model="form.notifications_enabled" />
      </div>
      <div class="flex items-center justify-between py-2">
        <div>
          <div class="font-medium text-gray-900">Email</div>
          <div class="text-sm text-gray-500">Email уведомления</div>
        </div>
        <input type="checkbox" v-model="form.email_notifications_enabled" />
      </div>
      <div class="flex items-center justify-between py-2">
        <div>
          <div class="font-medium text-gray-900">Push</div>
          <div class="text-sm text-gray-500">WebSocket push (real-time)</div>
        </div>
        <input type="checkbox" v-model="form.push_notifications_enabled" />
      </div>
      <div class="pt-4">
        <button
          type="button"
          class="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
          @click="save"
        >
          Сохранить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'

const store = useNotificationStore()
const form = reactive({
  notifications_enabled: true,
  email_notifications_enabled: true,
  push_notifications_enabled: true
})

const save = async () => {
  await store.updatePreferences(form)
}

onMounted(async () => {
  await store.fetchPreferences()
  if (store.preferences) {
    form.notifications_enabled = !!store.preferences.notifications_enabled
    form.email_notifications_enabled = !!store.preferences.email_notifications_enabled
    form.push_notifications_enabled = !!store.preferences.push_notifications_enabled
  }
})
</script>


