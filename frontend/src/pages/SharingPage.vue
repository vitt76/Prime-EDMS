// @ts-nocheck
<template>
<div class="sharing-page min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-neutral-900">Распространение</h1>
          <p class="mt-1 text-sm text-neutral-600">Управление публичными ссылками и кампаниями</p>
        </div>
        
        <!-- Create Dropdown -->
        <Menu as="div" class="relative">
          <MenuButton
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white text-sm font-semibold rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/25"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Создать
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  @click="openShareModal"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
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
                  @click="openEmailShareModal"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  @click="openCampaignModal"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
      
      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <div 
          class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3 cursor-pointer hover:shadow-md transition-shadow"
          @click="setActiveTab('all')"
        >
          <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.totalLinks }}</p>
            <p class="text-sm text-neutral-500">Всего ссылок</p>
          </div>
        </div>
        <div 
          class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3 cursor-pointer hover:shadow-md transition-shadow"
          @click="setActiveTab('active')"
        >
          <div class="w-12 h-12 bg-success-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.activeLinks }}</p>
            <p class="text-sm text-neutral-500">Активных</p>
          </div>
        </div>
        <div 
          class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3 cursor-pointer hover:shadow-md transition-shadow"
          @click="setActiveTab('expired')"
        >
          <div class="w-12 h-12 bg-warning-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.expiredLinks }}</p>
            <p class="text-sm text-neutral-500">Истекших</p>
          </div>
        </div>
      <div class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.totalViews.toLocaleString() }}</p>
            <p class="text-sm text-neutral-500">Просмотров</p>
          </div>
        </div>
        <div 
          class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3 cursor-pointer hover:shadow-md transition-shadow"
          @click="setActiveTab('campaigns')"
        >
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7h18M3 12h18M3 17h18" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.campaigns }}</p>
            <p class="text-sm text-neutral-500">Кампаний</p>
          </div>
        </div>
      </div>
      
      <!-- Tabs & Table Container -->
      <div class="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <!-- Tab Headers -->
        <div class="flex items-center border-b border-neutral-200">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            :class="[
              'relative flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'text-primary-600'
                : 'text-neutral-500 hover:text-neutral-700'
            ]"
            @click="setActiveTab(tab.id)"
          >
            <span>{{ tab.label }}</span>
            <span
              v-if="tab.count !== undefined"
              :class="[
                'px-2 py-0.5 text-xs rounded-full',
                activeTab === tab.id
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-neutral-100 text-neutral-600'
              ]"
            >
              {{ tab.count }}
            </span>
            <!-- Active indicator -->
            <div
              v-if="activeTab === tab.id"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
            />
          </button>
          
          <!-- Bulk Actions -->
          <Transition
            enter-active-class="transition ease-out duration-150"
            enter-from-class="opacity-0 translate-x-2"
            enter-to-class="opacity-100 translate-x-0"
            leave-active-class="transition ease-in duration-100"
            leave-from-class="opacity-100 translate-x-0"
            leave-to-class="opacity-0 translate-x-2"
          >
            <div v-if="selectedLinks.size > 0" class="ml-4 flex items-center gap-2 bg-primary-50 rounded-lg px-3 py-1.5">
              <span class="text-sm text-primary-700 font-medium">{{ selectedLinks.size }} выбрано</span>
              <button
                type="button"
                class="p-1.5 text-primary-600 hover:text-error-600 hover:bg-error-50 rounded transition-colors"
                title="Удалить выбранные"
                @click="bulkRevoke"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              <button
                type="button"
                class="p-1.5 text-primary-600 hover:text-neutral-600 hover:bg-neutral-100 rounded transition-colors"
                title="Снять выделение"
                @click="clearSelection"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </Transition>
          
          <!-- Search & Refresh -->
          <div class="ml-auto mr-4 flex items-center gap-3">
            <div class="relative">
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="tableSearch"
                type="text"
                placeholder="Поиск по имени, автору..."
                class="w-56 pl-9 pr-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              />
              <button
                v-if="tableSearch"
                type="button"
                class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-neutral-400 hover:text-neutral-600"
                @click="tableSearch = ''"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <button
              type="button"
              class="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
              @click="refreshData"
              :disabled="isLoading"
              title="Обновить"
            >
              <svg :class="['w-5 h-5', isLoading && 'animate-spin']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Tab Content -->
        <div class="p-0">
          <!-- Loading -->
          <div v-if="activeTab === 'campaigns'">
            <!-- Campaigns tab -->
            <div v-if="distributionStore.campaignsLoading" class="p-12 text-center">
              <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p class="text-sm text-neutral-500">Загрузка кампаний...</p>
            </div>
            <div v-else-if="distributionStore.campaignsError" class="p-12 text-center">
              <p class="text-sm text-error-600 mb-2">Ошибка: {{ distributionStore.campaignsError }}</p>
              <button
                type="button"
                class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
                @click="refreshCampaigns"
              >
                Повторить
              </button>
            </div>
            <div v-else-if="distributionStore.campaigns.length === 0" class="p-12 text-center">
              <svg class="mx-auto w-16 h-16 text-neutral-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7h18M3 12h18M3 17h18" />
              </svg>
              <h3 class="text-lg font-medium text-neutral-900 mb-2">Нет кампаний</h3>
              <p class="text-sm text-neutral-500 mb-4">Создайте кампанию, чтобы объединить несколько публикаций и ссылок.</p>
              <button
                type="button"
                class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
                @click="openCampaignModal"
              >
                Создать кампанию
              </button>
            </div>
            <div v-else class="p-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <div
                v-for="campaign in distributionStore.campaigns"
                :key="campaign.id"
                class="border border-neutral-200 rounded-xl p-4 bg-white hover:shadow-md transition-shadow"
              >
                <div class="flex items-start justify-between mb-2">
                  <div class="min-w-0">
                    <h3 class="text-base font-semibold text-neutral-900 truncate">
                      {{ campaign.title }}
                    </h3>
                    <p class="text-xs text-neutral-500 mt-0.5">
                      Создатель: {{ campaign.owner_username || '—' }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <span
                      class="px-2 py-0.5 text-xs rounded-full"
                      :class="campaign.state === 'active'
                        ? 'bg-success-100 text-success-700'
                        : campaign.state === 'draft'
                          ? 'bg-neutral-100 text-neutral-600'
                          : campaign.state === 'completed'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-warning-100 text-warning-700'"
                    >
                      {{ campaignStateLabel(campaign.state) }}
                    </span>
                    <button
                      type="button"
                      class="p-1 text-neutral-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                      title="Просмотреть кампанию"
                      @click="openCampaignDetails(campaign)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      class="p-1 text-neutral-400 hover:text-error-600 hover:bg-error-50 rounded-full transition-colors"
                      title="Удалить кампанию"
                      @click="deleteCampaign(campaign)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
                <p class="text-sm text-neutral-600 line-clamp-2 mb-3">{{ campaign.description || 'Без описания' }}</p>
                <div class="flex items-center gap-4 text-sm text-neutral-600 mb-3">
                  <span class="flex items-center gap-1.5">
                    <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ formatDate(campaign.created) }}
                  </span>
                  <span class="flex items-center gap-1.5">
                    <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7h18M3 12h18M3 17h18" />
                    </svg>
                    {{ campaign.assets_count ?? campaign.publications_count }} файлов
                  </span>
                </div>
                <div class="flex items-center gap-4 text-sm text-neutral-600">
                  <span class="flex items-center gap-1.5" title="Просмотры">
                    <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {{ formatNumber(campaign.total_views || 0) }}
                  </span>
                  <span class="flex items-center gap-1.5" title="Скачивания">
                    <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    {{ formatNumber(campaign.total_downloads || 0) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="isLoading && filteredLinks.length === 0" class="p-12 text-center">
            <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p class="text-sm text-neutral-500">Загрузка...</p>
          </div>
          
          <!-- Empty State -->
          <div v-else-if="filteredLinks.length === 0" class="p-12 text-center">
            <svg class="mx-auto w-16 h-16 text-neutral-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 class="text-lg font-medium text-neutral-900 mb-2">
              {{ tableSearch ? 'Ничего не найдено' : (activeTab === 'all' ? 'Нет публичных ссылок' : `Нет ${tabs.find(t => t.id === activeTab)?.label.toLowerCase()} ссылок`) }}
            </h3>
            <p class="text-sm text-neutral-500 mb-4">
              {{ tableSearch ? 'Попробуйте изменить параметры поиска' : 'Выберите активы в галерее и создайте ссылку для распространения' }}
            </p>
            <div v-if="distributionStore.sharedLinksError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-600">Ошибка загрузки: {{ distributionStore.sharedLinksError }}</p>
            </div>
            <div class="flex items-center justify-center gap-4">
              <router-link
                v-if="!tableSearch"
                to="/dam"
                class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
              >
                Перейти в галерею
              </router-link>
              <button
                v-if="!tableSearch"
                @click="showShareModal = true"
                class="inline-flex items-center gap-2 px-4 py-2 bg-neutral-100 text-neutral-700 text-sm font-medium rounded-lg hover:bg-neutral-200 transition-colors"
              >
                Создать ссылку
              </button>
            </div>
          </div>
          
          <!-- Table -->
          <table v-else class="w-full">
            <thead>
              <tr class="bg-neutral-50 border-b border-neutral-200">
                <th class="w-12 px-4 py-3">
                  <input
                    type="checkbox"
                    :checked="allSelected"
                    :indeterminate="someSelected && !allSelected"
                    class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                    @change="toggleSelectAll"
                  />
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Ссылка
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Создано
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Истекает
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Статистика
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Статус
                </th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neutral-100">
              <tr
                v-for="link in filteredLinks"
                :key="link.id"
                :class="[
                  'group transition-colors cursor-pointer',
                  selectedLinks.has(link.id) ? 'bg-primary-50' : 'hover:bg-neutral-50'
                ]"
                @click="navigateToDetail(link)"
              >
                <!-- Checkbox -->
                <td class="w-12 px-4 py-4" @click.stop>
                  <input
                    type="checkbox"
                    :checked="selectedLinks.has(link.id)"
                    class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                    @change="toggleSelectLink(link.id)"
                  />
                </td>
                
                <!-- Link Info with Thumbnail Stack -->
                <td class="px-4 py-4">
                  <div class="flex items-center gap-4">
                    <!-- Stacked Thumbnails -->
                    <div class="relative flex-shrink-0" style="width: 68px; height: 44px;">
                      <template v-if="link.assets && link.assets.length > 0">
                        <div
                          v-for="(asset, idx) in link.assets.slice(0, 3)"
                          :key="idx"
                          class="absolute rounded-lg overflow-hidden border-2 border-white shadow-sm transition-transform group-hover:scale-105"
                          :style="{
                            width: '44px',
                            height: '44px',
                            left: `${idx * 12}px`,
                            zIndex: 3 - idx,
                          }"
                        >
                          <img
                            :src="asset.thumbnail_url || 'https://via.placeholder.com/44'"
                            :alt="asset.label"
                            class="w-full h-full object-cover"
                            loading="lazy"
                          />
                        </div>
                        <!-- More indicator -->
                        <div
                          v-if="link.assets.length > 3"
                          class="absolute rounded-lg bg-neutral-800/90 text-white text-[10px] font-bold flex items-center justify-center border-2 border-white"
                          style="width: 44px; height: 44px; left: 36px; z-index: 0;"
                        >
                          +{{ link.assets.length - 3 }}
                        </div>
                      </template>
                      <!-- No assets placeholder -->
                      <div
                        v-else
                        class="w-11 h-11 rounded-lg bg-neutral-100 flex items-center justify-center"
                      >
                        <svg class="w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                    </div>
                    
                    <!-- Link Details -->
                    <div class="min-w-0">
                      <p class="text-sm font-medium text-neutral-900 truncate max-w-[220px] group-hover:text-primary-600 transition-colors">
                        {{ link.name }}
                      </p>
                      <div class="flex items-center gap-1.5 mt-0.5">
                        <code class="text-xs text-neutral-500 font-mono truncate max-w-[160px]">
                          {{ link.slug }}
                        </code>
                        <!-- Quick Copy inline -->
                        <button
                          type="button"
                          class="p-0.5 text-neutral-400 hover:text-primary-600 opacity-0 group-hover:opacity-100 transition-all"
                          title="Копировать ссылку"
                          @click.stop="copyLink(link)"
                        >
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </button>
                        <!-- Password indicator -->
                        <span v-if="link.password_protected" class="text-neutral-400" title="Защищено паролем">
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                          </svg>
                        </span>
                      </div>
                    </div>
                  </div>
                </td>
                
                <!-- Created -->
                <td class="px-4 py-4">
                  <p class="text-sm text-neutral-900">{{ formatDate(link.created_date) }}</p>
                  <p class="text-xs text-neutral-500">{{ link.created_by }}</p>
                </td>
                
                <!-- Expires -->
                <td class="px-4 py-4">
                  <p class="text-sm text-neutral-900">
                    {{ link.expires_date ? formatDate(link.expires_date) : '∞ Бессрочно' }}
                  </p>
                  <p
                    v-if="link.expires_date && getDaysUntilExpiry(link.expires_date) <= 7 && getDaysUntilExpiry(link.expires_date) > 0"
                    class="text-xs text-warning-600 font-medium"
                  >
                    ⏰ через {{ getDaysUntilExpiry(link.expires_date) }} дн.
                  </p>
                </td>
                
                <!-- Stats -->
                <td class="px-4 py-4">
                  <div class="flex items-center gap-4 text-sm text-neutral-600">
                    <span class="flex items-center gap-1.5" title="Просмотры">
                      <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      {{ formatNumber(link.views || 0) }}
                    </span>
                    <span class="flex items-center gap-1.5" title="Скачивания">
                      <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      {{ formatNumber(link.downloads || 0) }}
                    </span>
                  </div>
                </td>
                
                <!-- Status (Clickable) -->
                <td class="px-4 py-4" @click.stop>
                  <button
                    type="button"
                    :class="[
                      'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold cursor-pointer transition-all hover:ring-2 hover:ring-offset-1',
                      getStatusClasses(link.status)
                    ]"
                    @click="filterByStatus(link.status)"
                    :title="`Показать все ${getStatusLabel(link.status).toLowerCase()} ссылки`"
                  >
                    <span :class="getStatusDotClass(link.status)" />
                    {{ getStatusLabel(link.status) }}
                  </button>
                </td>
                
                <!-- Actions -->
                <td class="px-4 py-4 text-right" @click.stop>
                  <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <!-- Copy -->
                    <button
                      v-if="link.status === 'active'"
                      type="button"
                      class="p-2 text-neutral-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                      title="Копировать ссылку"
                      @click="copyLink(link)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <!-- Edit -->
                    <button
                      v-if="link.status !== 'revoked'"
                      type="button"
                      class="p-2 text-neutral-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Редактировать"
                      @click="editLink(link)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <!-- Revoke -->
                    <button
                      v-if="link.status !== 'revoked'"
                      type="button"
                      class="p-2 text-neutral-500 hover:text-error-600 hover:bg-error-50 rounded-lg transition-colors"
                      title="Отозвать ссылку"
                      @click="revokeLink(link)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Revoke Confirmation Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showRevokeModal && revokingLink" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="closeRevokeModal" />
          <div class="relative w-full max-w-sm bg-white rounded-2xl shadow-xl p-6 text-center">
            <div class="w-14 h-14 mx-auto bg-error-100 rounded-full flex items-center justify-center mb-4">
              <svg class="w-7 h-7 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-neutral-900 mb-2">Отозвать ссылку?</h3>
            <p class="text-sm text-neutral-600 mb-6">
              Ссылка <span class="font-medium">"{{ revokingLink.name }}"</span> перестанет работать. Это действие нельзя отменить.
            </p>
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="closeRevokeModal"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-error-600 rounded-xl hover:bg-error-700 transition-colors"
                @click="confirmRevoke"
              >
                Отозвать
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
    
    <!-- Bulk Revoke Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showBulkRevokeModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="closeBulkRevokeModal" />
          <div class="relative w-full max-w-sm bg-white rounded-2xl shadow-xl p-6 text-center">
            <div class="w-14 h-14 mx-auto bg-error-100 rounded-full flex items-center justify-center mb-4">
              <svg class="w-7 h-7 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-neutral-900 mb-2">Отозвать {{ selectedLinks.size }} ссылок?</h3>
            <p class="text-sm text-neutral-600 mb-6">
              Выбранные ссылки перестанут работать. Это действие нельзя отменить.
            </p>
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="closeBulkRevokeModal"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-error-600 rounded-xl hover:bg-error-700 transition-colors"
                @click="confirmBulkRevoke"
              >
                Отозвать все
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
    
    <!-- Edit Link Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showEditModal && editingLink" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="closeEditModal" />
          <div class="relative w-full max-w-md bg-white rounded-2xl shadow-xl p-6">
            <h3 class="text-lg font-semibold text-neutral-900 mb-4">Редактировать ссылку</h3>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-neutral-700 mb-1">Название</label>
                <input
                  v-model="editForm.name"
                  type="text"
                  class="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-neutral-700 mb-1">Срок действия</label>
                <input
                  v-model="editForm.expires_date"
                  type="date"
                  class="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div class="flex items-center gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="editForm.allow_download"
                    type="checkbox"
                    class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="text-sm text-neutral-700">Разрешить скачивание</span>
                </label>
                
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="editForm.allow_comment"
                    type="checkbox"
                    class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="text-sm text-neutral-700">Комментарии</span>
                </label>
              </div>
            </div>
            
            <div class="flex gap-3 mt-6">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="closeEditModal"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-colors"
                @click="saveEdit"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
    
    <!-- Share Modal -->
    <ShareModal
      :is-open="showShareModal"
      :assets="[]"
      @close="showShareModal = false"
      @success="handleShareSuccess"
    />

    <!-- Campaign Create/Edit Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showCampaignModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="closeCampaignModal" />
          <div class="relative w-full max-w-md bg-white rounded-2xl shadow-xl p-6">
            <h3 class="text-lg font-semibold text-neutral-900 mb-4">
              {{ campaignModalMode === 'create' ? 'Новая кампания' : 'Редактировать кампанию' }}
            </h3>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-neutral-700 mb-1">Название</label>
                <input
                  v-model="campaignForm.title"
                  type="text"
                  class="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Например, Летняя коллекция 2026"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-neutral-700 mb-1">Описание</label>
                <textarea
                  v-model="campaignForm.description"
                  rows="3"
                  class="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                  placeholder="Краткое описание цели кампании"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-neutral-700 mb-1">Статус</label>
                <select
                  v-model="campaignForm.state"
                  class="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
                >
                  <option value="draft">Черновик</option>
                  <option value="active">Активна</option>
                  <option value="completed">Завершена</option>
                  <option value="paused">На паузе</option>
                </select>
              </div>
            </div>

            <div class="flex gap-3 mt-6">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="closeCampaignModal"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-colors"
                @click="saveCampaign"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Campaign Details Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showCampaignDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="closeCampaignDetailsModal" />
          <div class="relative w-full max-w-2xl bg-white rounded-2xl shadow-xl p-6 max-h-[80vh] overflow-y-auto">
            <div class="flex items-start justify-between mb-4">
              <div>
                <h3 class="text-lg font-semibold text-neutral-900">
                  Детали кампании
                </h3>
                <p v-if="campaignDetails" class="text-sm text-neutral-500 mt-1">
                  {{ campaignDetails.title || 'Без названия' }}
                </p>
              </div>
              <button
                type="button"
                class="p-1 text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100 rounded-full transition-colors"
                @click="closeCampaignDetailsModal"
              >
                <span class="sr-only">Закрыть</span>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div v-if="campaignDetailsLoading" class="py-12 text-center">
              <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p class="text-sm text-neutral-500">Загрузка деталей кампании...</p>
            </div>
            <div v-else-if="campaignDetails" class="space-y-6">
              <div class="space-y-2">
                <div class="flex items-center gap-2">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="campaignDetails.state === 'active'
                      ? 'bg-success-100 text-success-700'
                      : campaignDetails.state === 'draft'
                        ? 'bg-neutral-100 text-neutral-600'
                        : campaignDetails.state === 'completed'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-warning-100 text-warning-700'"
                  >
                    {{ campaignStateLabel(campaignDetails.state) }}
                  </span>
                  <span class="text-xs text-neutral-500">
                    Создана: {{ formatDate(campaignDetails.created) }}
                  </span>
                </div>
                <p class="text-sm text-neutral-700">
                  {{ campaignDetails.description || 'Без описания' }}
                </p>
              </div>

              <div class="border-t border-neutral-200 pt-4">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-medium text-neutral-900">
                    Файлы в кампании
                  </h4>
                  <div class="flex items-center gap-3">
                    <span class="text-xs text-neutral-500">
                      {{ (campaignDetailsAssets.length) || 0 }} файлов
                    </span>
                    <button
                      v-if="selectedDocumentIds.length > 0"
                      type="button"
                      class="px-2 py-1 text-xs font-medium text-primary-700 bg-primary-50 rounded-md hover:bg-primary-100 transition-colors"
                      @click="addSelectedDocumentsToCampaign"
                    >
                      Добавить выбранные ({{ selectedDocumentIds.length }})
                    </button>
                  </div>
                </div>

                <div v-if="campaignDetailsAssets.length > 0" class="space-y-2">
                  <div
                    v-for="asset in campaignDetailsAssets"
                    :key="asset.id"
                    class="flex items-center justify-between px-3 py-2 rounded-lg border border-neutral-200 bg-neutral-50"
                  >
                    <div class="flex items-center gap-3 min-w-0">
                      <img
                        :src="getAssetPreviewUrl(asset)"
                        class="w-12 h-12 rounded-lg object-cover bg-neutral-100 border border-neutral-200 flex-shrink-0"
                        :alt="asset.document_label || `Документ #${asset.document_id}`"
                      />
                      <div class="min-w-0">
                        <p class="text-sm font-medium text-neutral-900 truncate">
                          <a
                            :href="getAssetDocumentUrl(asset)"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="hover:underline"
                          >
                            {{ asset.document_label || `Документ #${asset.document_id}` }}
                          </a>
                        </p>
                        <p class="text-xs text-neutral-500">
                          document_id: {{ asset.document_id }} · file_id: {{ asset.document_file_id }}
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      class="p-1 text-neutral-400 hover:text-error-600 hover:bg-error-50 rounded-full transition-colors"
                      title="Удалить файл из кампании"
                      @click="removeAssetFromCampaign(asset)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
                <div v-else class="py-6 text-center text-sm text-neutral-500">
                  В кампанию пока не добавлено ни одного файла.
                </div>
              </div>

              <div class="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  class="px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
                  @click="saveCampaignAssets"
                >
                  Сохранить изменения файлов
                </button>
                <button
                  type="button"
                  class="px-3 py-2 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-lg hover:bg-neutral-200 transition-colors"
                  @click="editCampaignFromDetails"
                >
                  Редактировать кампанию
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
/**
 * SharingPage.vue - Unified Distribution Hub
 * 
 * AUDIT FIXES IMPLEMENTED:
 * ✅ Added bulk selection (checkboxes)
 * ✅ Added row click navigation to detail
 * ✅ Enhanced search to include creator name
 * ✅ Added Edit button with modal
 * ✅ Added Quick Copy button inline with slug
 * ✅ Added bulk delete functionality
 * ✅ Stats cards are now clickable to filter
 * ✅ Added Email Share option in create dropdown
 * ✅ Password indicator icon on protected links
 * ✅ Status dots for visual feedback
 * ✅ Number formatting for stats
 * ✅ Hover states with opacity transitions
 */

import { ref, computed, reactive, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { useDistributionStore, type SharedLink } from '@/stores/distributionStore'
import { distributionService } from '@/services/distributionService'
import { useNotificationStore } from '@/stores/notificationStore'
import { useAssetStore } from '@/stores/assetStore'
import ShareModal from '@/components/DAM/ShareModal.vue'
import { apiService } from '@/services/apiService'
import { resolveAssetImageUrl } from '@/utils/imageUtils'

// ============================================================================
// STORES & ROUTER
// ============================================================================

const router = useRouter()
const route = useRoute()
const distributionStore = useDistributionStore()
const notificationStore = useNotificationStore()
const assetStore = useAssetStore()

// ============================================================================
// STATE
// ============================================================================

type TabId = 'all' | 'active' | 'expired' | 'campaigns'

const activeTab = ref<TabId>('all')
const tableSearch = ref('')
const isLoading = ref(false)

// Single revoke
const showRevokeModal = ref(false)
const revokingLink = ref<SharedLink | null>(null)

// Bulk selection
const selectedLinks = ref<Set<number>>(new Set())
const showBulkRevokeModal = ref(false)

// Edit modal
const showEditModal = ref(false)
const editingLink = ref<SharedLink | null>(null)
const editForm = reactive({
  name: '',
  expires_date: '',
  allow_download: true,
  allow_comment: false
})

// Create modal
const showShareModal = ref(false)

// Campaign create/edit modal
const showCampaignModal = ref(false)
const campaignModalMode = ref<'create' | 'edit'>('create')
const editingCampaignId = ref<number | null>(null)
const campaignForm = reactive({
  title: '',
  description: '',
  state: 'draft' as 'draft' | 'active' | 'completed' | 'paused'
})

const selectedDocumentIds = computed(() => Array.from(assetStore.selectedAssets))

// Campaign details modal
const showCampaignDetailsModal = ref(false)
const campaignDetailsLoading = ref(false)
const campaignDetails = ref<any | null>(null)
const campaignDetailsAssets = ref<any[]>([])
const campaignAssetPreviews = ref<Record<string, string>>({})

// ============================================================================
// COMPUTED
// ============================================================================

const tabs = computed(() => [
  { id: 'all' as const, label: 'Все ссылки', count: distributionStore.sharedLinks.length },
  { id: 'active' as const, label: 'Активные', count: distributionStore.sharedLinks.filter(l => l.status === 'active').length },
  { id: 'expired' as const, label: 'Истекшие', count: distributionStore.sharedLinks.filter(l => l.status === 'expired' || l.status === 'revoked').length },
  { id: 'campaigns' as const, label: 'Кампании', count: distributionStore.campaigns.length },
])

const stats = computed(() => ({
  totalLinks: distributionStore.sharedLinks.length,
  activeLinks: distributionStore.sharedLinks.filter(l => l.status === 'active').length,
  expiredLinks: distributionStore.sharedLinks.filter(l => l.status === 'expired' || l.status === 'revoked').length,
  totalViews: distributionStore.sharedLinks.reduce((sum, l) => sum + (l.views || 0), 0),
  campaigns: distributionStore.campaigns.length
}))

const filteredLinks = computed(() => {
  let links = [...distributionStore.sharedLinks]
  
  // Filter by tab (only for link tabs)
  if (activeTab.value === 'active') {
    links = links.filter(l => l.status === 'active')
  } else if (activeTab.value === 'expired') {
    links = links.filter(l => l.status === 'expired' || l.status === 'revoked')
  }
  
  // Filter by search (name, slug, AND creator)
  if (tableSearch.value) {
    const query = tableSearch.value.toLowerCase()
    links = links.filter(l => 
      l.name.toLowerCase().includes(query) ||
      l.slug.toLowerCase().includes(query) ||
      l.created_by.toLowerCase().includes(query)
    )
  }
  
  return links
})

// Selection helpers
const allSelected = computed(() => 
  filteredLinks.value.length > 0 && 
  filteredLinks.value.every(l => selectedLinks.value.has(l.id))
)

const someSelected = computed(() => 
  filteredLinks.value.some(l => selectedLinks.value.has(l.id))
)

// ============================================================================
// METHODS - Navigation & Filtering
// ============================================================================

function setActiveTab(tab: TabId) {
  activeTab.value = tab
  router.replace({ query: { ...route.query, tab } })
}

function filterByStatus(status: SharedLink['status']) {
  if (status === 'active') {
    setActiveTab('active')
  } else {
    setActiveTab('expired')
  }
}

function navigateToDetail(link: SharedLink) {
  // Navigate to link detail page (mock route)
  router.push({ path: `/sharing/${link.id}`, query: { slug: link.slug } })
  
  // For now, show toast since detail page might not exist
  notificationStore.addNotification({
    type: 'info',
    title: link.name,
    message: `UUID: ${link.slug} • ${link.assets?.length || 0} активов • ${formatNumber(link.views)} просмотров`
  })
}

// ============================================================================
// METHODS - Selection
// ============================================================================

function toggleSelectLink(id: number) {
  if (selectedLinks.value.has(id)) {
    selectedLinks.value.delete(id)
  } else {
    selectedLinks.value.add(id)
  }
  // Force reactivity
  selectedLinks.value = new Set(selectedLinks.value)
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedLinks.value.clear()
  } else {
    filteredLinks.value.forEach(l => selectedLinks.value.add(l.id))
  }
  selectedLinks.value = new Set(selectedLinks.value)
}

function clearSelection() {
  selectedLinks.value.clear()
  selectedLinks.value = new Set(selectedLinks.value)
}

// ============================================================================
// METHODS - CRUD Operations
// ============================================================================

async function refreshData() {
  isLoading.value = true
  try {
    console.log('[SharingPage] Refreshing data, calling fetchSharedLinks...')
    await distributionStore.fetchSharedLinks()
    console.log('[SharingPage] Data refreshed, links count:', distributionStore.sharedLinks.length)
  } finally {
    isLoading.value = false
  }
}

async function copyLink(link: SharedLink) {
  try {
    await navigator.clipboard.writeText(link.url)
    notificationStore.addNotification({
      type: 'success',
      title: 'Скопировано',
      message: 'Ссылка скопирована в буфер обмена'
    })
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось скопировать ссылку'
    })
  }
}

// Single revoke
function revokeLink(link: SharedLink) {
  revokingLink.value = link
  showRevokeModal.value = true
}

function closeRevokeModal() {
  showRevokeModal.value = false
  revokingLink.value = null
}

async function confirmRevoke() {
  if (!revokingLink.value) return
  
  try {
    await distributionStore.revokeSharedLink(revokingLink.value.id)
    notificationStore.addNotification({
      type: 'success',
      title: 'Отозвано',
      message: 'Публичная ссылка больше недоступна'
    })
    closeRevokeModal()
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось отозвать ссылку'
    })
  }
}

// Bulk revoke
function bulkRevoke() {
  if (selectedLinks.value.size === 0) return
  showBulkRevokeModal.value = true
}

function closeBulkRevokeModal() {
  showBulkRevokeModal.value = false
}

async function confirmBulkRevoke() {
  const ids = Array.from(selectedLinks.value)
  let successCount = 0
  
  for (const id of ids) {
    try {
      await distributionStore.revokeSharedLink(id)
      successCount++
    } catch {
      // Continue with others
    }
  }
  
  notificationStore.addNotification({
    type: successCount === ids.length ? 'success' : 'warning',
    title: 'Отозвано',
    message: `${successCount} из ${ids.length} ссылок отозвано`
  })
  
  clearSelection()
  closeBulkRevokeModal()
}

// Edit
function editLink(link: SharedLink) {
  editingLink.value = link
  editForm.name = link.name
  editForm.expires_date = link.expires_date ? link.expires_date.split('T')[0] : ''
  editForm.allow_download = link.allow_download
  editForm.allow_comment = link.allow_comment
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  editingLink.value = null
}

async function saveEdit() {
  if (!editingLink.value) return
  
  try {
    await distributionStore.updateSharedLink(editingLink.value.id, {
      name: editForm.name,
      expires_date: editForm.expires_date || null,
      allow_download: editForm.allow_download,
      allow_comment: editForm.allow_comment
    })
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Сохранено',
      message: 'Настройки ссылки обновлены'
    })
    
    closeEditModal()
    await refreshData()
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось сохранить изменения'
    })
  }
}

// Create modals
function openShareModal() {
  showShareModal.value = true
}

function openEmailShareModal() {
  notificationStore.addNotification({
    type: 'info',
    title: 'Email рассылка',
    message: 'Функционал email рассылки будет доступен в следующем обновлении'
  })
}

async function openCampaignModal() {
  // Для создания кампании обязательно должны быть выбраны активы
  if (selectedDocumentIds.value.length === 0) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Нет выбранных активов',
      message: 'Сначала выберите документы в галерее, затем создайте кампанию.'
    })
    router.push('/dam')
    return
  }

  campaignModalMode.value = 'create'
  editingCampaignId.value = null
  campaignForm.title = ''
  campaignForm.description = ''
  campaignForm.state = 'draft'
  showCampaignModal.value = true
}

function closeCampaignModal() {
  showCampaignModal.value = false
}

async function refreshCampaigns() {
  await distributionStore.fetchCampaigns()
}

function handleShareSuccess(url: string) {
  showShareModal.value = false
  refreshData()
}

// ============================================================================
// METHODS - Formatting & Helpers
// ============================================================================

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

function getDaysUntilExpiry(dateStr: string): number {
  const now = new Date()
  const expiry = new Date(dateStr)
  const diffTime = expiry.getTime() - now.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

function getStatusClasses(status: SharedLink['status']): string {
  const classes = {
    active: 'bg-success-100 text-success-700 hover:ring-success-300',
    expired: 'bg-warning-100 text-warning-700 hover:ring-warning-300',
    revoked: 'bg-neutral-100 text-neutral-600 hover:ring-neutral-300'
  }
  return classes[status] || classes.revoked
}

function getStatusDotClass(status: SharedLink['status']): string {
  const classes = {
    active: 'w-1.5 h-1.5 rounded-full bg-success-500',
    expired: 'w-1.5 h-1.5 rounded-full bg-warning-500',
    revoked: 'w-1.5 h-1.5 rounded-full bg-neutral-400'
  }
  return classes[status] || classes.revoked
}

function getStatusLabel(status: SharedLink['status']): string {
  const labels = {
    active: 'Активна',
    expired: 'Истекла',
    revoked: 'Отозвана'
  }
  return labels[status] || 'Неизвестно'
}

function campaignStateLabel(state: string): string {
  const labels: Record<string, string> = {
    draft: 'Черновик',
    active: 'Активна',
    completed: 'Завершена',
    paused: 'На паузе'
  }
  return labels[state] || 'Неизвестно'
}

// ============================================================================
// Campaign actions (details / edit / delete)
// ============================================================================

async function editCampaign(campaign: any) {
  campaignModalMode.value = 'edit'
  editingCampaignId.value = campaign.id
  campaignForm.title = campaign.title
  campaignForm.description = campaign.description || ''
  campaignForm.state = campaign.state || 'draft'
  showCampaignModal.value = true
}

async function deleteCampaign(campaign: any) {
  if (!window.confirm(`Удалить кампанию "${campaign.title}"?`)) {
    return
  }

  try {
    const ok = await distributionStore.deleteCampaign(campaign.id)
    if (ok) {
      notificationStore.addNotification({
        type: 'success',
        title: 'Кампания удалена',
        message: campaign.title
      })
      await refreshCampaigns()
    }
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось удалить кампанию'
    })
    console.error('Failed to delete campaign:', error)
  }
}

async function openCampaignDetails(campaign: DistributionCampaign) {
  showCampaignDetailsModal.value = true
  campaignDetailsLoading.value = true
  campaignDetails.value = null
  campaignDetailsAssets.value = []
  // Очистим старые превью
  Object.values(campaignAssetPreviews.value).forEach(url => {
    try {
      URL.revokeObjectURL(url)
    } catch {
      // ignore
    }
  })
  campaignAssetPreviews.value = {}

  try {
    const details: any = await distributionService.getCampaign(campaign.id)
    campaignDetails.value = details
    campaignDetailsAssets.value = Array.isArray(details.assets) ? [...details.assets] : []
    await loadCampaignAssetPreviews()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось загрузить детали кампании'
    })
    console.error('Failed to load campaign details:', error)
    showCampaignDetailsModal.value = false
  } finally {
    campaignDetailsLoading.value = false
  }
}

function closeCampaignDetailsModal() {
  // Освобождаем objectURL-ы превью
  Object.values(campaignAssetPreviews.value).forEach(url => {
    try {
      URL.revokeObjectURL(url)
    } catch {
      // ignore
    }
  })
  campaignAssetPreviews.value = {}
  showCampaignDetailsModal.value = false
}

async function saveCampaignAssets() {
  if (!campaignDetails.value) return

  const documentIds = campaignDetailsAssets.value
    .map((asset: any) => asset.document_id)
    .filter((id: any) => typeof id === 'number')

  try {
    const updated: any = await distributionService.updateCampaign(
      campaignDetails.value.id,
      { document_ids: documentIds }
    )
    campaignDetails.value = updated
    campaignDetailsAssets.value = Array.isArray(updated.assets) ? [...updated.assets] : []
    await loadCampaignAssetPreviews()
    // Обновляем список кампаний, чтобы пересчитался assets_count
    await distributionStore.fetchCampaigns()
    notificationStore.addNotification({
      type: 'success',
      title: 'Кампания обновлена',
      message: 'Состав файлов кампании сохранён'
    })
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось сохранить состав файлов кампании'
    })
    console.error('Failed to save campaign assets:', error)
  }
}

function removeAssetFromCampaign(asset: any) {
  campaignDetailsAssets.value = campaignDetailsAssets.value.filter(a => a.id !== asset.id)
}

function addSelectedDocumentsToCampaign() {
  if (!selectedDocumentIds.value.length) return

  const existingIds = new Set(
    campaignDetailsAssets.value
      .map((asset: any) => asset.document_id)
      .filter((id: any) => typeof id === 'number')
  )

  const now = Date.now()
  selectedDocumentIds.value.forEach((docId, index) => {
    if (!existingIds.has(docId)) {
      campaignDetailsAssets.value.push({
        id: `tmp-${now}-${index}-${docId}`,
        document_id: docId,
        document_label: `Документ #${docId}`,
        document_file_id: null
      })
    }
  })
}

function assetPreviewKey(asset: any, resolvedFileId?: number | null): string {
  const filePart = resolvedFileId ?? asset.document_file_id ?? asset.file_latest_id ?? asset.file_id
  const docPart = asset.document_id ?? asset.id
  return `${docPart || 'doc'}-${filePart || 'file'}`
}

function getAssetPreviewUrl(asset: any): string {
  const key = assetPreviewKey(asset)
  const blobUrl = campaignAssetPreviews.value[key]
  if (blobUrl) {
    return blobUrl
  }

  // Fallback: используем ту же логику превью, что и в галерее/коллекциях,
  // чтобы всегда показывать "актуальную" версию документа.
  const pseudoAsset: any = {
    id: asset.document_id || asset.id,
    version_active_id: asset.version_active_id || asset.version_id || asset.version?.id,
    file_latest_id: asset.document_file_id || asset.file_latest_id || asset.file_id,
    thumbnail_url: asset.thumbnail_url,
    preview_url: asset.preview_url,
    download_url: asset.download_url
  }

  return resolveAssetImageUrl(pseudoAsset)
}

async function loadCampaignAssetPreviews() {
  const previews: Record<string, string> = {}

  for (const asset of campaignDetailsAssets.value) {
    if (!asset?.document_id) continue

    const docId = asset.document_id
    // Приоритет — "текущий" файл, который приходит из бэкенда (document_file_id).
    // Только если его нет, пробуем подтянуть последний файл по timestamp.
    let fileId: number | null =
      asset.document_file_id || asset.file_latest_id || asset.file_id || null

    if (!fileId) {
      try {
        const filesResponse: any = await apiService.get(
          `/api/v4/documents/${docId}/files/`,
          { params: { page_size: 1, ordering: '-timestamp' } } as any,
          false
        )
        const results = Array.isArray(filesResponse?.results)
          ? filesResponse.results
          : Array.isArray(filesResponse)
            ? filesResponse
            : []
        fileId = results[0]?.id || null
      } catch (e) {
        // Если запрос файлов не удался, оставляем fileId как null и переходим к следующему asset.
        fileId = null
      }
    }

    if (!fileId) continue

    // Обновляем идентификатор файла в объекте asset, чтобы ключ превью
    // совпадал между загрузкой и рендерингом (используем актуальный файл).
    asset.document_file_id = fileId
    asset.file_latest_id = fileId

    // Для активной версии пробуем добавить путь на всякий случай
    const versionId = asset.version_active_id || asset.version_id || asset.version?.id

    const paths: string[] = []
    // 1) прямой download (даёт актуальный файл, как в галерее)
    paths.push(`/api/v4/documents/${docId}/files/${fileId}/download/`)
    // 2) страница актуального файла
    paths.push(`/api/v4/documents/${docId}/files/${fileId}/pages/1/image/?width=600`)
    // 3) страница активной версии (если есть)
    if (versionId) {
      paths.push(`/api/v4/documents/${docId}/versions/${versionId}/pages/1/image/?width=600`)
    }

    for (const path of paths) {
      try {
        const blob = await apiService.get<Blob>(
          path,
          { responseType: 'blob' } as any,
          false
        )
        const objectUrl = window.URL.createObjectURL(blob)
        // Ключ должен совпадать с getAssetPreviewUrl(asset),
        // который вызывает assetPreviewKey(asset) без fileId.
        previews[assetPreviewKey(asset)] = objectUrl
        break
      } catch (e) {
        // try next path
        continue
      }
    }
  }

  // Освобождаем старые objectURL-ы
  Object.values(campaignAssetPreviews.value).forEach(url => {
    try {
      URL.revokeObjectURL(url)
    } catch {
      // ignore
    }
  })

  campaignAssetPreviews.value = previews
}

function getAssetDocumentUrl(asset: any): string {
  if (asset?.document_id) {
    // SPA-роут на карточку ассета в DAM
    return `/dam/assets/${asset.document_id}`
  }
  return '#'
}

async function editCampaignFromDetails() {
  if (!campaignDetails.value) return
  await editCampaign(campaignDetails.value)
  showCampaignDetailsModal.value = false
}

async function saveCampaign() {
  if (!campaignForm.title.trim()) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Название кампании обязательно'
    })
    return
  }

  try {
    if (campaignModalMode.value === 'create') {
      const campaign = await distributionStore.createCampaign({
        title: campaignForm.title.trim(),
        description: campaignForm.description.trim() || undefined,
        document_ids: selectedDocumentIds.value
      })
      if (campaign) {
        notificationStore.addNotification({
          type: 'success',
          title: 'Кампания создана',
          message: campaign.title
        })
      }
    } else if (campaignModalMode.value === 'edit' && editingCampaignId.value !== null) {
      const updated = await distributionStore.updateCampaign(editingCampaignId.value, {
        title: campaignForm.title.trim(),
        description: campaignForm.description.trim() || '',
        state: campaignForm.state
      })
      if (updated) {
        notificationStore.addNotification({
          type: 'success',
          title: 'Кампания обновлена',
          message: updated.title
        })
      }
    }

    await refreshCampaigns()
    closeCampaignModal()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось сохранить кампанию'
    })
    console.error('Failed to save campaign:', error)
  }
}

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(async () => {
  // Check URL for tab parameter
  const tabParam = route.query.tab as TabId
  if (tabParam && ['all', 'active', 'expired', 'campaigns'].includes(tabParam)) {
    activeTab.value = tabParam
  }
  
  // Загружаем и ссылки, и кампании при инициализации,
  // чтобы счётчики и табы сразу отображали актуальные данные
  await Promise.all([
    refreshData(),
    refreshCampaigns()
  ])

  // Если пришли с галереи с выбранными активами для создания кампании
  if (route.query.from === 'assets' && selectedDocumentIds.value.length > 0) {
    activeTab.value = 'campaigns'
    await nextTick()
    await openCampaignModal()
    // Убираем служебный флаг из URL
    router.replace({ query: { ...route.query, from: undefined, tab: 'campaigns' } })
  }
})

// Watch for route changes
watch(() => route.query.tab, async (newTab) => {
  if (newTab && ['all', 'active', 'expired', 'campaigns'].includes(newTab as string)) {
    activeTab.value = newTab as TabId
    if (activeTab.value === 'campaigns') {
      await refreshCampaigns()
    }
  }
})
</script>

<style scoped>
.sharing-page {
  padding-top: calc(var(--header-height, 64px));
}

/* Indeterminate checkbox styling */
input[type="checkbox"]:indeterminate {
  background-color: #6366f1;
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M4 8h8'/%3e%3c/svg%3e");
}
</style>
