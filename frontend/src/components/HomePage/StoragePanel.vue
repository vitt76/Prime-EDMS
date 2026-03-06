<template>
  <div class="storage-panel bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 p-5">
    <h2 class="text-lg font-semibold text-neutral-900 mb-4 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-xl text-neutral-500">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7c-2 0-3 1-3 3z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 12h16" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 7v5" />
          </svg>
        </span> 
        Хранилище
      </div>
      <router-link
        v-if="isAdmin"
        :to="{ name: 'admin-storage' }"
        class="text-xs font-medium text-primary-600 hover:text-primary-700"
      >
        Управление
      </router-link>
    </h2>

    <div v-if="homeStore.isLoading && !homeStore.storageStats" class="animate-pulse">
      <div class="flex justify-between mb-2">
        <div class="h-3 bg-neutral-200 rounded w-1/4"></div>
        <div class="h-3 bg-neutral-200 rounded w-1/4"></div>
      </div>
      <div class="h-2 bg-neutral-200 rounded-full w-full mb-3"></div>
      <div class="h-3 bg-neutral-200 rounded w-1/2"></div>
    </div>

    <div v-else-if="homeStore.storageStats">
      <div class="flex justify-between text-sm mb-2 font-medium">
        <span class="text-neutral-900">{{ formatBytes(homeStore.storageStats.used_bytes) }}</span>
        <span class="text-neutral-500">
          <template v-if="homeStore.storageStats.is_unlimited">без лимита</template>
          <template v-else>из {{ formatBytes(homeStore.storageStats.limit_bytes) }}</template>
        </span>
      </div>
      
      <!-- Progress Bar -->
      <div class="w-full bg-neutral-100 rounded-full h-2 mb-3 overflow-hidden flex">
        <div 
          class="bg-primary-500 h-2 rounded-full transition-all duration-500" 
          :class="{ 'bg-error': (homeStore.storageStats.percentage ?? 0) >= 90, 'bg-warning': (homeStore.storageStats.percentage ?? 0) >= 75 && (homeStore.storageStats.percentage ?? 0) < 90 }"
          :style="{ width: `${Math.min(homeStore.storageStats.percentage ?? 0, 100)}%` }"
        ></div>
      </div>

      <p class="text-xs text-neutral-500">
        <template v-if="homeStore.storageStats.is_unlimited">
          Организация использует хранилище без жесткой квоты
        </template>
        <template v-else>
          Использовано {{ homeStore.storageStats.percentage ?? 0 }}% от вашей квоты
        </template>
      </p>

      <div v-if="(homeStore.storageStats.percentage ?? 0) >= 90" class="mt-3 p-2 bg-error/10 text-error text-xs rounded border border-error">
        Внимание: Квота хранилища почти исчерпана. Обратитесь к администратору или удалите старые файлы.
      </div>
    </div>

    <div v-else class="text-sm text-neutral-500">
      Метрика хранилища сейчас недоступна.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useHomeStore } from '@/stores/homeStore'
import { useAuthStore } from '@/stores/authStore'

const homeStore = useHomeStore()
const authStore = useAuthStore()

const isAdmin = computed(() => {
  return authStore.user?.is_superuser || authStore.user?.is_staff
})

function formatBytes(bytes: number | null, decimals = 1) {
  if (bytes === null) return 'Без лимита'
  if (!+bytes) return '0 Байт'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Байт', 'КБ', 'МБ', 'ГБ', 'ТБ', 'ПБ']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}
</script>