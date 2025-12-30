<template>
  <div class="border-b border-neutral-200 bg-white">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between gap-4 py-4">
        <div class="flex items-center gap-3">
          <div class="text-lg font-semibold text-neutral-900">Аналитика</div>
        </div>
      </div>

      <!-- Primary tabs -->
      <div class="flex items-center gap-2 overflow-x-auto pb-2">
        <RouterLink
          v-for="tab in primaryTabs"
          :key="tab.to"
          :to="tab.to"
          :class="[
            'px-3 py-2 text-sm rounded-md transition-colors whitespace-nowrap',
            isActivePrimary(tab.match)
              ? 'bg-primary-50 text-primary-700'
              : 'text-neutral-600 hover:bg-neutral-50'
          ]"
        >
          {{ tab.label }}
        </RouterLink>
      </div>

      <!-- Secondary tabs (contextual) -->
      <div v-if="secondaryTabs.length" class="flex items-center gap-2 overflow-x-auto pb-3">
        <RouterLink
          v-for="tab in secondaryTabs"
          :key="tab.to"
          :to="tab.to"
          :class="[
            'px-3 py-1.5 text-sm rounded-md transition-colors whitespace-nowrap border',
            isActiveSecondary(tab.to)
              ? 'border-primary-300 bg-primary-50 text-primary-700'
              : 'border-neutral-200 text-neutral-600 hover:bg-neutral-50'
          ]"
        >
          {{ tab.label }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const primaryTabs = [
  { label: 'Обзор', to: '/analytics/overview', match: '/analytics/overview' },
  { label: 'Маркетинг', to: '/analytics/marketing/campaigns', match: '/analytics/marketing' },
  { label: 'Контент AI', to: '/analytics/content-ai', match: '/analytics/content-ai' },
  { label: 'Операции', to: '/analytics/operations/users', match: '/analytics/operations' },
]

const secondaryTabs = computed(() => {
  const path = route.path || ''
  if (path.startsWith('/analytics/marketing')) {
    return [
      { label: 'Кампании', to: '/analytics/marketing/campaigns' },
      { label: 'ROI', to: '/analytics/marketing/roi' },
      { label: 'Дистрибуция', to: '/analytics/marketing/distribution' },
    ]
  }
  if (path.startsWith('/analytics/operations')) {
    return [
      { label: 'Пользователи', to: '/analytics/operations/users' },
      { label: 'Согласования', to: '/analytics/operations/approvals' },
    ]
  }
  return []
})

function isActivePrimary(matchPrefix: string): boolean {
  const path = route.path || ''
  return path === matchPrefix || path.startsWith(matchPrefix + '/')
}

function isActiveSecondary(to: string): boolean {
  const path = route.path || ''
  return path === to || path.startsWith(to + '/')
}
</script>


