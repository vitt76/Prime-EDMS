<template>
  <div class="kpi-bar grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-8 mb-2">
    <!-- Card 1: Assets -->
    <div class="kpi-card bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 p-5 flex flex-col justify-between hover:shadow-md transition-shadow">
      <div class="flex justify-between items-start mb-2">
        <h3 class="text-sm font-medium text-neutral-500">Всего документов</h3>
      </div>
      <div class="flex items-end gap-2 mb-1">
        <span class="text-2xl font-bold text-neutral-900">
          {{ homeStore.documentsStats?.total ?? 0 }}
        </span>
        <span class="text-sm pb-1 text-neutral-500">документов</span>
      </div>
      <div class="text-sm mb-4">
        <span :class="documentsGrowthClass" class="font-medium">
          +{{ homeStore.documentsStats?.new_7days ?? 0 }}
        </span>
        <span class="text-neutral-500"> за 7 дней</span>
      </div>
      <router-link 
        :to="{ name: 'dam-gallery' }"
        class="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        <span>&rarr; Обзор</span>
      </router-link>
    </div>

    <!-- Card 2: AI Analyses -->
    <div class="kpi-card bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 p-5 flex flex-col justify-between hover:shadow-md transition-shadow">
      <div class="flex justify-between items-start mb-2">
        <h3 class="text-sm font-medium text-neutral-500">Завершённых анализов</h3>
      </div>
      <div class="flex items-end gap-2 mb-1">
        <span class="text-2xl font-bold text-neutral-900">
          {{ homeStore.aiStats?.analyzed ?? 0 }}
        </span>
        <span class="text-sm pb-1 text-neutral-500">с AI анализом</span>
      </div>
      <div class="text-sm mb-4 text-neutral-500">
        {{ homeStore.aiStats?.queued ?? 0 }} в очереди
      </div>
      <button 
        @click="openAIBulk"
        class="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        <span>⚡ Запустить недостающие</span>
      </button>
    </div>

    <!-- Card 3: Action Required -->
    <div class="kpi-card bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 p-5 flex flex-col justify-between hover:shadow-md transition-shadow">
      <div class="flex justify-between items-start mb-2">
        <h3 class="text-sm font-medium text-neutral-500">Требуется действие</h3>
      </div>
      <div class="flex items-end gap-2 mb-1">
        <span class="text-2xl font-bold text-neutral-900">
          {{ homeStore.inboxStats?.unread_total ?? 0 }}
        </span>
      </div>
      <div class="text-sm mb-4 text-neutral-500 flex gap-1 truncate">
        <span>{{ homeStore.inboxStats?.comments_new ?? 0 }} комм.</span> /
        <span>{{ homeStore.inboxStats?.approvals_pending ?? 0 }} одобр.</span> /
        <span>{{ homeStore.inboxStats?.collections_shared ?? 0 }} кол.</span>
      </div>
      <button 
        @click="scrollToInbox"
        class="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        <span>📬 Открыть</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useHomeStore } from '@/stores/homeStore'
// Optionally import event bus or store logic to open AI bulk modal

const homeStore = useHomeStore()
const router = useRouter()

const documentsGrowthClass = computed(() => {
  const new7 = homeStore.documentsStats?.new_7days ?? 0
  return new7 > 0 ? 'text-success' : 'text-neutral-500'
})

function openAIBulk() {
  router.push({ name: 'dam-gallery', query: { status: 'untagged' } })
}

function scrollToInbox() {
  const inboxEl = document.getElementById('my-inbox-section')
  if (inboxEl) {
    inboxEl.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>