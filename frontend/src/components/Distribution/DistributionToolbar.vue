<template>
  <div class="mb-6">
    <!-- Desktop -->
    <div class="hidden md:flex items-center gap-4">
      <!-- Left: title -->
      <div class="min-w-[220px]">
        <h1 class="text-xl font-semibold text-neutral-900">Распространение</h1>
        <p class="mt-0.5 text-sm text-neutral-600">Управление публичными ссылками и кампаниями</p>
      </div>

      <!-- Middle: chips -->
      <div class="flex-1 flex items-center gap-2 min-w-0">
        <StatusChip
          label="Все ссылки"
          :count="stats.totalLinks"
          :active="activeTab === 'all'"
          tone="neutral"
          @click="emit('selectTab', 'all')"
        >
          <template #icon>
            <IconLink class="w-4 h-4" />
          </template>
        </StatusChip>

        <StatusChip
          label="Активные"
          :count="stats.activeLinks"
          :active="activeTab === 'active'"
          tone="success"
          @click="emit('selectTab', 'active')"
        />

        <StatusChip
          label="Истекшие"
          :count="stats.expiredLinks"
          :active="activeTab === 'expired'"
          tone="warning"
          @click="emit('selectTab', 'expired')"
        />

        <StatusChip
          label="Кампании"
          :count="stats.campaigns"
          :active="activeTab === 'campaigns'"
          tone="neutral"
          @click="emit('selectTab', 'campaigns')"
        />

        <!-- Views: informational + optional analytics shortcut -->
        <button
          type="button"
          class="ml-2 inline-flex items-center gap-1.5 text-sm text-neutral-600 hover:text-neutral-900 transition-colors whitespace-nowrap"
          title="Открыть аналитику по просмотрам"
          @click="emit('goAnalytics', { tab: 'marketing', metric: 'views' })"
        >
          <IconEye class="w-4 h-4 text-neutral-400" />
          <span>Просмотры</span>
          <span class="font-semibold text-neutral-900">{{ formatCompact(stats.totalViews) }}</span>
        </button>
      </div>

      <!-- Right: primary action -->
      <div class="flex items-center justify-end">
        <Menu as="div" class="relative">
          <MenuButton
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white text-sm font-semibold rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/25"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Создать
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </MenuButton>

          <Transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95"
          >
            <MenuItems class="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-neutral-200 py-2 z-10">
              <MenuItem v-slot="{ active }">
                <button
                  :class="[
                    'w-full px-4 py-3 text-left',
                    active ? 'bg-neutral-50' : ''
                  ]"
                  @click="emit('createShareLink')"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                      <IconLink class="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-900">Публичная ссылка</p>
                      <p class="text-xs text-neutral-500">Поделиться активами по URL</p>
                    </div>
                  </div>
                </button>
              </MenuItem>
              <MenuItem v-slot="{ active }">
                <button
                  :class="[
                    'w-full px-4 py-3 text-left',
                    active ? 'bg-neutral-50' : ''
                  ]"
                  @click="emit('createEmailShare')"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-900">Email рассылка</p>
                      <p class="text-xs text-neutral-500">Отправить активы по email</p>
                    </div>
                  </div>
                </button>
              </MenuItem>
              <MenuItem v-slot="{ active }">
                <button
                  :class="[
                    'w-full px-4 py-3 text-left',
                    active ? 'bg-neutral-50' : ''
                  ]"
                  @click="emit('createCampaign')"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-900">Кампания</p>
                      <p class="text-xs text-neutral-500">Многоканальное распространение</p>
                    </div>
                  </div>
                </button>
              </MenuItem>
            </MenuItems>
          </Transition>
        </Menu>
      </div>
    </div>

    <!-- Mobile -->
    <div class="md:hidden">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h1 class="text-xl font-semibold text-neutral-900">Распространение</h1>
          <p class="mt-0.5 text-sm text-neutral-600">Публичные ссылки и кампании</p>
        </div>
      </div>

      <div class="mt-3 -mx-4 px-4 overflow-x-auto no-scrollbar">
        <div class="flex items-center gap-2 w-max pb-1">
          <StatusChip label="Все" :count="stats.totalLinks" :active="activeTab === 'all'" tone="neutral" @click="emit('selectTab', 'all')">
            <template #icon><IconLink class="w-4 h-4" /></template>
          </StatusChip>
          <StatusChip label="Активные" :count="stats.activeLinks" :active="activeTab === 'active'" tone="success" @click="emit('selectTab', 'active')" />
          <StatusChip label="Истекшие" :count="stats.expiredLinks" :active="activeTab === 'expired'" tone="warning" @click="emit('selectTab', 'expired')" />
          <StatusChip label="Кампании" :count="stats.campaigns" :active="activeTab === 'campaigns'" tone="neutral" @click="emit('selectTab', 'campaigns')" />
          <button
            type="button"
            class="inline-flex items-center gap-1.5 px-3 py-2 rounded-full bg-transparent text-sm text-neutral-600"
            @click="emit('goAnalytics', { tab: 'marketing', metric: 'views' })"
          >
            <IconEye class="w-4 h-4 text-neutral-400" />
            <span>Просмотры</span>
            <span class="font-semibold text-neutral-900">{{ formatCompact(stats.totalViews) }}</span>
          </button>
        </div>
      </div>

      <div class="mt-4">
        <Menu as="div" class="relative">
          <MenuButton
            class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 text-white text-sm font-semibold rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/25"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Создать
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </MenuButton>

          <Transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95"
          >
            <MenuItems class="absolute left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-neutral-200 py-2 z-10">
              <MenuItem v-slot="{ active }">
                <button
                  :class="[
                    'w-full px-4 py-3 text-left',
                    active ? 'bg-neutral-50' : ''
                  ]"
                  @click="emit('createShareLink')"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                      <IconLink class="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-900">Публичная ссылка</p>
                      <p class="text-xs text-neutral-500">Поделиться активами по URL</p>
                    </div>
                  </div>
                </button>
              </MenuItem>
              <MenuItem v-slot="{ active }">
                <button
                  :class="[
                    'w-full px-4 py-3 text-left',
                    active ? 'bg-neutral-50' : ''
                  ]"
                  @click="emit('createEmailShare')"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-900">Email рассылка</p>
                      <p class="text-xs text-neutral-500">Отправить активы по email</p>
                    </div>
                  </div>
                </button>
              </MenuItem>
              <MenuItem v-slot="{ active }">
                <button
                  :class="[
                    'w-full px-4 py-3 text-left',
                    active ? 'bg-neutral-50' : ''
                  ]"
                  @click="emit('createCampaign')"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-900">Кампания</p>
                      <p class="text-xs text-neutral-500">Многоканальное распространение</p>
                    </div>
                  </div>
                </button>
              </MenuItem>
            </MenuItems>
          </Transition>
        </Menu>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'

import IconEye from '@/components/Common/icons/IconEye.vue'
import IconLink from '@/components/Common/icons/IconLink.vue'
import StatusChip from './DistributionToolbarChip.vue'

type TabId = 'all' | 'active' | 'expired' | 'campaigns'

const props = defineProps<{
  activeTab: TabId
  stats: {
    totalLinks: number
    activeLinks: number
    expiredLinks: number
    totalViews: number
    campaigns: number
  }
}>()

const emit = defineEmits<{
  selectTab: [tab: TabId]
  createShareLink: []
  createEmailShare: []
  createCampaign: []
  goAnalytics: [params: { tab: 'marketing'; section?: 'campaigns' | 'distribution'; metric?: 'views' }]
}>()

function formatCompact(value: number): string {
  const n = Number(value || 0)
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}
</script>

<style scoped>
.no-scrollbar {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
.no-scrollbar::-webkit-scrollbar {
  display: none; /* Chrome, Safari and Opera */
}
</style>


