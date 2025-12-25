<template>
  <div
    class="px-4 py-3 border-b border-gray-100 hover:bg-gray-50 flex gap-3"
    :class="notification.state === 'SENT' ? 'bg-indigo-50/30' : ''"
  >
    <div class="mt-1">
      <span
        v-if="notification.state === 'SENT'"
        class="inline-block w-2 h-2 bg-indigo-600 rounded-full"
        title="Непрочитано"
      />
    </div>
    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between gap-2">
        <div class="font-medium text-sm text-gray-900 truncate">
          {{ notification.title }}
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="notification.state === 'SENT'"
            class="text-xs text-indigo-600 hover:text-indigo-800"
            @click="$emit('read', notification.id)"
          >
            Прочитано
          </button>
          <button class="text-xs text-gray-500 hover:text-gray-700" @click="$emit('delete', notification.id)">
            Удалить
          </button>
        </div>
      </div>
      <div class="text-xs text-gray-600 mt-1 line-clamp-2">
        {{ notification.message }}
      </div>
      <div class="text-[11px] text-gray-400 mt-1">
        {{ notification.created_at }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NotificationCenterItem } from '@/stores/notificationStore'

defineProps<{ notification: NotificationCenterItem }>()
defineEmits<{ read: [id: number]; delete: [id: number] }>()
</script>


