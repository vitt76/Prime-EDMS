<template>
  <div class="min-h-screen bg-neutral-100 dark:bg-neutral-900">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center min-h-screen">
      <div class="flex flex-col items-center gap-4">
        <svg class="w-12 h-12 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <p class="text-neutral-600 dark:text-neutral-400">Загрузка актива...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
          <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-neutral-900 dark:text-white mb-2">Актив не найден</h2>
        <p class="text-neutral-600 dark:text-neutral-400 mb-4">{{ error }}</p>
        <router-link
          to="/dam"
          class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Вернуться в галерею
        </router-link>
      </div>
    </div>

    <!-- Asset Content -->
  <div v-else-if="asset" class="asset-detail-page flex flex-col h-screen">
      <!-- Top Bar -->
      <header class="flex items-center justify-between px-6 py-4 bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 shrink-0">
        <div class="flex items-center gap-4">
          <router-link
            to="/dam"
            class="flex items-center gap-2 px-3 py-2 text-sm font-medium text-neutral-600 dark:text-neutral-400 
                   hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-700 
                   rounded-lg transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Назад в галерею
          </router-link>
          <span class="text-neutral-300 dark:text-neutral-600">|</span>
          <h1 class="text-lg font-semibold text-neutral-900 dark:text-white truncate max-w-md">
            {{ asset.label }}
          </h1>
        </div>
        <div class="flex items-center gap-2">
          <!-- Download As Dropdown -->
          <Menu as="div" class="relative">
            <MenuButton
              class="flex items-center gap-2 px-4 py-2 text-sm font-medium
                     bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300
                     hover:bg-neutral-200 dark:hover:bg-neutral-600
                     rounded-lg transition-colors"
            >
              <ArrowDownTrayIcon class="w-4 h-4" />
              Скачать
              <ChevronDownIcon class="w-4 h-4" />
            </MenuButton>

            <transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <MenuItems
                class="absolute right-0 mt-2 w-56 origin-top-right rounded-lg bg-white dark:bg-neutral-800 
                       shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-20"
              >
                <div class="py-1">
                  <div class="px-3 py-2 border-b border-neutral-100 dark:border-neutral-700">
                    <p class="text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">
                      Скачать как
                    </p>
                  </div>
                  <MenuItem v-slot="{ active }">
                    <button
                      :class="[
                        active ? 'bg-neutral-100 dark:bg-neutral-700' : '',
                        'w-full text-left px-4 py-2 text-sm text-neutral-700 dark:text-neutral-300 flex items-center justify-between'
                      ]"
                      @click="handleDownloadAs('original')"
                    >
                      <div class="flex items-center gap-2">
                        <DocumentIcon class="w-4 h-4 text-neutral-500" />
                        <span>Оригинал</span>
                      </div>
                      <span class="text-xs text-neutral-400">
                        {{ formatFileSize(asset?.file_details?.size || asset?.size || 0) }}
                      </span>
                    </button>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <button
                      :class="[
                        active ? 'bg-neutral-100 dark:bg-neutral-700' : '',
                        'w-full text-left px-4 py-2 text-sm text-neutral-700 dark:text-neutral-300 flex items-center justify-between'
                      ]"
                      @click="handleDownloadAs('low_res')"
                    >
                      <div class="flex items-center gap-2">
                        <PhotoIcon class="w-4 h-4 text-blue-500" />
                        <span>Low Res (JPG, 72dpi)</span>
                      </div>
                      <span class="text-xs text-neutral-400">~500KB</span>
                    </button>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <button
                      :class="[
                        active ? 'bg-neutral-100 dark:bg-neutral-700' : '',
                        'w-full text-left px-4 py-2 text-sm text-neutral-700 dark:text-neutral-300 flex items-center justify-between'
                      ]"
                      @click="handleDownloadAs('high_res')"
                    >
                      <div class="flex items-center gap-2">
                        <PhotoIcon class="w-4 h-4 text-green-500" />
                        <span>High Res (PNG, 300dpi)</span>
                      </div>
                      <span class="text-xs text-neutral-400">~5MB</span>
                    </button>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <button
                      :class="[
                        active ? 'bg-neutral-100 dark:bg-neutral-700' : '',
                        'w-full text-left px-4 py-2 text-sm text-neutral-700 dark:text-neutral-300 flex items-center justify-between'
                      ]"
                      @click="handleDownloadAs('pdf')"
                    >
                      <div class="flex items-center gap-2">
                        <DocumentTextIcon class="w-4 h-4 text-red-500" />
                        <span>PDF (конвертированный)</span>
                      </div>
                      <span class="text-xs text-neutral-400">~1MB</span>
                    </button>
                  </MenuItem>
                </div>
              </MenuItems>
            </transition>
          </Menu>

          <!-- Edit / Transform Button -->
          <button
            v-if="isImage"
            class="flex items-center gap-2 px-4 py-2 text-sm font-medium
                   bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300
                   hover:bg-purple-200 dark:hover:bg-purple-900/50
                   rounded-lg transition-colors"
            @click="showMediaEditor = true"
          >
            <PencilSquareIcon class="w-4 h-4" />
            Редактировать
          </button>

          <button
            class="flex items-center gap-2 px-4 py-2 text-sm font-medium
                   bg-primary-600 text-white
                   hover:bg-primary-700
                   rounded-lg transition-colors"
            @click="handleShare"
          >
            <ShareIcon class="w-4 h-4" />
            Поделиться
          </button>
        </div>
      </header>

      <!-- Main Content -->
      <div class="flex flex-1 overflow-hidden">
        <!-- Preview Area (70%) -->
        <div class="flex-1 flex items-center justify-center bg-neutral-900 relative overflow-hidden">
          <!-- Preview (image or previewable doc) -->
          <div
            v-if="showPreview"
            class="relative w-full h-full flex items-center justify-center p-8"
          >
            <button
              class="absolute top-4 right-4 p-2.5 rounded-full bg-white/90 text-neutral-700 hover:bg-white hover:scale-105 transition"
              :class="{ 'text-red-500': isFavorite }"
              @click.stop="toggleFavorite"
              aria-label="Добавить в избранное"
              type="button"
            >
              <svg class="w-5 h-5" :fill="isFavorite ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </button>
            <img
              v-if="!previewError"
              :key="`${asset?.id || 'asset'}:${previewResolved}`"
              :src="previewResolved"
              :alt="asset.label"
              class="max-w-full max-h-full object-contain rounded-lg shadow-2xl transition-transform duration-200"
              :style="{ transform: `scale(${zoom}) rotate(${rotation}deg)` }"
              @error="handlePreviewImageError"
            />
            <div
              v-else
              class="w-full h-full flex items-center justify-center bg-neutral-800 rounded-lg"
            >
              <svg class="w-16 h-16 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>

          <!-- Video Preview -->
          <div v-else-if="isVideo" class="relative w-full h-full flex items-center justify-center p-8">
            <video
              controls
              class="max-w-full max-h-full rounded-lg shadow-2xl"
              :poster="asset.thumbnail_url"
            >
              <source :src="asset.preview_url || '#'" type="video/mp4" />
              Ваш браузер не поддерживает видео.
            </video>
          </div>

          <!-- Audio Preview -->
          <div v-else-if="isAudio" class="relative w-full h-full flex items-center justify-center p-8">
            <div class="bg-white rounded-lg shadow-2xl p-8 w-full max-w-lg">
              <div class="flex items-center gap-4 mb-6">
                <div class="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                  <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-neutral-900">{{ asset.label }}</h3>
                  <p class="text-sm text-neutral-600">{{ formatDuration((asset.metadata as Record<string, number>)?.duration) }}</p>
                </div>
              </div>
              <audio controls class="w-full">
                <source :src="asset.preview_url || '#'" type="audio/mpeg" />
              </audio>
            </div>
          </div>

          <!-- Zoom Controls (for images) -->
          <div
            v-if="isImage"
            class="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 
                   bg-black/60 backdrop-blur-xl rounded-xl px-3 py-2"
          >
            <button
              class="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              @click="zoomOut"
              :disabled="zoom <= 0.5"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
              </svg>
            </button>
            <span class="text-white text-sm font-medium min-w-[3rem] text-center">
              {{ Math.round(zoom * 100) }}%
            </span>
            <button
              class="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              @click="zoomIn"
              :disabled="zoom >= 3"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
              </svg>
            </button>
            <span class="w-px h-6 bg-white/20"></span>
            <button
              class="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              @click="rotateLeft"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button
              class="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              @click="resetView"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Sidebar (30%) -->
        <aside class="w-[400px] shrink-0 bg-white dark:bg-neutral-800 border-l border-neutral-200 dark:border-neutral-700 flex flex-col overflow-hidden">
          <!-- Workflow Widget (Collapsible) -->
          <div class="p-4 border-b border-neutral-200 dark:border-neutral-700 shrink-0">
            <div class="rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900/40 shadow-sm overflow-hidden">
              <Disclosure v-slot="{ open }" :default-open="!collapsedSections.status">
                <DisclosureButton
                  class="w-full flex items-center justify-between px-4 py-3 text-left border-b border-neutral-100 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                  @click="collapsedSections.status = !open"
                >
                  <h3 class="text-sm font-semibold text-neutral-900 dark:text-white flex items-center gap-2">
                    <ArrowPathRoundedSquareIcon class="w-4 h-4 text-neutral-500" />
                    Статус и согласование
                  </h3>
                  <ChevronDownIcon
                    :class="['w-4 h-4 text-neutral-500 transition-transform', open ? 'rotate-180' : '']"
                  />
                </DisclosureButton>

                <DisclosurePanel class="p-0">
                  <WorkflowWidget
                    :asset-id="assetId"
                    @status-change="handleWorkflowStatusChange"
                  />
                </DisclosurePanel>
              </Disclosure>
            </div>
          </div>

          <!-- AI Insights Widget -->
          <div class="p-4 border-b border-neutral-200 dark:border-neutral-700 shrink-0 max-h-[400px] overflow-y-auto">
            <AIInsightsWidget 
              :asset-id="assetId"
              @tags-updated="handleTagsUpdated"
              @analysis-complete="handleAnalysisComplete"
            />
          </div>

          <!-- Tabs -->
          <div class="flex border-b border-neutral-200 dark:border-neutral-700 shrink-0 sticky top-0 z-10 bg-white dark:bg-neutral-800">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              class="flex-1 px-4 py-3 text-sm font-medium transition-colors relative"
              :class="activeTab === tab.id 
                ? 'text-primary-600 dark:text-primary-400' 
                : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'"
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
              <span
                v-if="activeTab === tab.id"
                class="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600 dark:bg-primary-400"
              ></span>
            </button>
          </div>

          <!-- Tab Content -->
          <div class="flex-1 overflow-y-auto">
            <!-- Info Tab -->
            <div v-if="activeTab === 'info'" class="p-5 space-y-6">
              <!-- Basic Info -->
              <section class="rounded-xl border border-neutral-200 dark:border-neutral-700 p-4 bg-white dark:bg-neutral-900/40 shadow-sm">
                <h3 class="text-sm font-semibold text-neutral-900 dark:text-white mb-3">Основная информация</h3>
                <dl class="space-y-3">
                  <div class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Имя файла</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white font-medium truncate max-w-[180px]">{{ asset.filename }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Размер</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ formatFileSize(asset.size) }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Тип</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ asset.mime_type }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Добавлен</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ formatDate(asset.file_details?.uploaded_date || asset.date_added) }}</dd>
                  </div>
                  <div v-if="asset.metadata?.width && asset.metadata?.height" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Размеры</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ asset.metadata.width }} × {{ asset.metadata.height }} px</dd>
                  </div>
                </dl>
              </section>

              <!-- Description -->
              <section v-if="asset.description">
                <h3 class="text-sm font-semibold text-neutral-900 dark:text-white mb-2">Описание</h3>
                <p class="text-sm text-neutral-700 dark:text-neutral-300 whitespace-pre-line">
                  {{ asset.description }}
                </p>
              </section>

              <!-- EXIF Data (for images) -->
              <section v-if="extendedAsset?.exif" class="rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900/40 shadow-sm overflow-hidden">
                <Disclosure v-slot="{ open }" :default-open="!collapsedSections.exif">
                  <DisclosureButton
                    class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors"
                    @click="collapsedSections.exif = !open"
                  >
                    <h3 class="text-sm font-semibold text-neutral-900 dark:text-white">EXIF / Камера</h3>
                    <ChevronDownIcon
                      :class="['w-4 h-4 text-neutral-500 transition-transform', open ? 'rotate-180' : '']"
                    />
                  </DisclosureButton>

                  <DisclosurePanel class="px-4 pb-4">
                    <dl class="space-y-3">
                  <div v-if="extendedAsset.exif.make" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Камера</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ extendedAsset.exif.make }} {{ extendedAsset.exif.model }}</dd>
                  </div>
                  <div v-if="extendedAsset.exif.lens" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Объектив</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ extendedAsset.exif.lens }}</dd>
                  </div>
                  <div v-if="extendedAsset.exif.focalLength" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Фокус. расст.</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ extendedAsset.exif.focalLength }}</dd>
                  </div>
                  <div v-if="extendedAsset.exif.aperture" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Диафрагма</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ extendedAsset.exif.aperture }}</dd>
                  </div>
                  <div v-if="extendedAsset.exif.shutterSpeed" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Выдержка</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ extendedAsset.exif.shutterSpeed }}</dd>
                  </div>
                  <div v-if="extendedAsset.exif.iso" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">ISO</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ extendedAsset.exif.iso }}</dd>
                  </div>
                  <div v-if="extendedAsset.exif.colorSpace" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">Цвет. простр.</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ extendedAsset.exif.colorSpace }}</dd>
                  </div>
                  <div v-if="extendedAsset.exif.dpi" class="flex justify-between">
                    <dt class="text-sm text-neutral-500 dark:text-neutral-400">DPI</dt>
                    <dd class="text-sm text-neutral-900 dark:text-white">{{ extendedAsset.exif.dpi }}</dd>
                  </div>
                    </dl>
                  </DisclosurePanel>
                </Disclosure>
              </section>

              <!-- Tags -->
              <section v-if="asset.tags && asset.tags.length > 0" class="rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900/40 shadow-sm overflow-hidden">
                <Disclosure v-slot="{ open }" :default-open="!collapsedSections.tags">
                  <DisclosureButton
                    class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors"
                    @click="collapsedSections.tags = !open"
                  >
                    <h3 class="text-sm font-semibold text-neutral-900 dark:text-white">Теги</h3>
                    <ChevronDownIcon
                      :class="['w-4 h-4 text-neutral-500 transition-transform', open ? 'rotate-180' : '']"
                    />
                  </DisclosureButton>

                  <DisclosurePanel class="px-4 pb-4">
                    <div class="flex flex-wrap gap-2">
                    <span
                      v-for="tag in asset.tags"
                      :key="tag"
                      class="px-2.5 py-1 text-xs font-medium rounded-full 
                             bg-primary-100 dark:bg-primary-900/30 
                             text-primary-700 dark:text-primary-300"
                    >
                      {{ tag }}
                    </span>
                    </div>
                  </DisclosurePanel>
                </Disclosure>
              </section>

              <!-- AI Analysis -->
              <section v-if="asset.ai_analysis?.status === 'completed'" class="rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900/40 shadow-sm overflow-hidden">
                <Disclosure v-slot="{ open }" :default-open="!collapsedSections.ai">
                  <DisclosureButton
                    class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors"
                    @click="collapsedSections.ai = !open"
                  >
                    <h3 class="text-sm font-semibold text-neutral-900 dark:text-white">AI Анализ</h3>
                    <ChevronDownIcon
                      :class="['w-4 h-4 text-neutral-500 transition-transform', open ? 'rotate-180' : '']"
                    />
                  </DisclosureButton>

                  <DisclosurePanel class="px-4 pb-4">
                    <p v-if="asset.ai_analysis.ai_description" class="text-sm text-neutral-600 dark:text-neutral-400 mb-3">
                      {{ asset.ai_analysis.ai_description }}
                    </p>
                    <div v-if="asset.ai_analysis.tags?.length" class="flex flex-wrap gap-1.5">
                      <span
                        v-for="tag in asset.ai_analysis.tags"
                        :key="tag"
                        class="px-2 py-0.5 text-xs rounded bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300"
                      >
                        {{ tag }}
                      </span>
                    </div>
                  </DisclosurePanel>
                </Disclosure>
              </section>
            </div>

            <!-- Metadata Tab -->
            <div v-if="activeTab === 'metadata'" class="p-5">
              <MetadataEditor 
                :asset-id="assetId"
                :document-type="documentType"
                @save="handleMetadataSave"
              />
            </div>

            <!-- Versions Tab -->
            <div v-if="activeTab === 'versions'" class="p-5">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-sm font-semibold text-neutral-900 dark:text-white">История версий</h3>
                <button
                  class="text-sm text-primary-600 dark:text-primary-400 hover:underline"
                  @click="handleUploadNewVersion"
                >
                  + Новая версия
                </button>
              </div>
              
              <div v-if="!versions.length" class="text-sm text-neutral-500 dark:text-neutral-400">
                Версий нет или они недоступны.
              </div>
              <div v-else class="space-y-3">
                <div
                  v-for="version in versions"
                  :key="version.id"
                  class="p-3 rounded-xl border transition-colors"
                  :class="version.is_current 
                    ? 'border-primary-300 dark:border-primary-700 bg-primary-50 dark:bg-primary-900/20' 
                    : 'border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/50'"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-lg bg-neutral-200 dark:bg-neutral-600 flex items-center justify-center text-sm font-semibold text-neutral-600 dark:text-neutral-300">
                        v{{ versions.indexOf(version) + 1 }}
                      </div>
                      <div>
                        <p class="text-sm font-medium text-neutral-900 dark:text-white">
                          {{ version.filename }}
                          <span v-if="version.is_current" class="ml-2 text-xs text-primary-600 dark:text-primary-400">(текущая)</span>
                        </p>
                        <p class="text-xs text-neutral-500 dark:text-neutral-400">
                          {{ version.uploaded_by }} • {{ formatDate(version.uploaded_date) }}
                        </p>
                      </div>
                    </div>
                    <button
                      v-if="!version.is_current"
                      class="text-xs text-primary-600 dark:text-primary-400 hover:underline"
                      @click.stop="handleRevertVersion(version)"
                    >
                      Откатить
                    </button>
                  </div>
                </div>
              </div>
            </div>

          <!-- Other File Types (icon fallback) -->
          <div v-else-if="activeTab !== 'metadata' && activeTab !== 'comments' && activeTab !== 'usage'" class="flex-1 flex items-start justify-center px-4 pb-6">
            <div class="w-full max-w-xl sticky top-4 rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900/60 shadow-sm p-5 flex flex-col gap-3">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-lg bg-neutral-200 dark:bg-neutral-700 flex items-center justify-center text-sm font-semibold text-neutral-600 dark:text-neutral-200">
                  {{ fileExtension || 'FILE' }}
                </div>
                <div class="min-w-0">
                  <p class="text-base font-semibold text-neutral-900 dark:text-white truncate">
                    {{ asset.file_details?.filename || asset.filename || asset.label || 'Файл' }}
                  </p>
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">Предпросмотр недоступен</p>
                </div>
              </div>
              <p v-if="asset.description" class="text-sm text-neutral-600 dark:text-neutral-300 leading-relaxed">
                {{ asset.description }}
              </p>
              <div class="flex flex-wrap gap-2 text-sm text-neutral-600 dark:text-neutral-300">
                <span v-if="fileExtension" class="px-2 py-1 rounded bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
                  Тип: {{ fileExtension.toUpperCase() }}
                </span>
                <span v-if="asset.file_details?.size" class="px-2 py-1 rounded bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
                  {{ formatFileSize(asset.file_details.size) }}
                </span>
              </div>
              <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 sm:items-center">
                <button
                  class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  @click="handleDownload"
                >
                  Скачать
                </button>
                <button
                  class="px-4 py-2 border border-neutral-200 dark:border-neutral-700 rounded-lg text-neutral-700 dark:text-neutral-200 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
                  @click="activeTab = 'metadata'"
                >
                  Открыть метаданные
                </button>
              </div>
              <div class="flex items-center justify-between text-xs text-neutral-500 dark:text-neutral-400">
                <span>Файл без предпросмотра</span>
                <button
                  class="hover:text-primary-600 dark:hover:text-primary-400"
                  @click="scrollToTop"
                >
                  К началу
                </button>
              </div>
            </div>
          </div>

            <!-- Comments Tab -->
            <div v-if="activeTab === 'comments'" class="flex flex-col h-full">
              <div class="flex-1 overflow-y-auto p-5 space-y-4">
                <!-- Loading State -->
                <div v-if="isLoadingComments" class="flex items-center justify-center py-8">
                  <svg class="w-6 h-6 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                  <span class="ml-2 text-sm text-neutral-500 dark:text-neutral-400">Загрузка комментариев...</span>
                </div>

                <!-- Empty State -->
                <div v-else-if="!isLoadingComments && comments.length === 0" class="text-center py-8">
                  <svg class="w-12 h-12 mx-auto text-neutral-300 dark:text-neutral-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">Нет комментариев</p>
                </div>

                <!-- Comments List -->
                <div
                  v-for="comment in comments"
                  :key="comment.id"
                  class="flex gap-3 group"
                >
                  <img
                    :src="comment.author_avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(comment.author)"
                    :alt="comment.author"
                    class="w-8 h-8 rounded-full object-cover shrink-0"
                  />
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between mb-1">
                      <div class="flex items-center gap-2 flex-wrap">
                        <span class="text-sm font-medium text-neutral-900 dark:text-white">{{ comment.author }}</span>
                        <span class="text-xs text-neutral-500 dark:text-neutral-400">{{ formatRelativeTime(comment.created_date) }}</span>
                        <span v-if="comment.edited" class="text-xs text-neutral-400">(изменено)</span>
                      </div>
                      <!-- Action Buttons (only for comment author) -->
                      <div v-if="canEditComment(comment)" class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          v-if="editingCommentId !== comment.id"
                          @click="startEditComment(comment)"
                          class="p-1.5 text-neutral-500 hover:text-primary-600 dark:hover:text-primary-400 rounded hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                          title="Редактировать"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          v-if="editingCommentId !== comment.id"
                          @click="deleteComment(comment.id)"
                          class="p-1.5 text-neutral-500 hover:text-red-600 dark:hover:text-red-400 rounded hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                          title="Удалить"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    <!-- Edit Mode -->
                    <div v-if="editingCommentId === comment.id" class="space-y-2">
                      <textarea
                        v-model="editingCommentText"
                        rows="3"
                        class="w-full px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600
                               bg-white dark:bg-neutral-900
                               text-neutral-900 dark:text-white
                               placeholder-neutral-400
                               focus:ring-2 focus:ring-primary-500 focus:border-transparent
                               transition-all text-sm resize-none"
                        placeholder="Редактировать комментарий..."
                        @keydown.ctrl.enter="saveEditComment"
                        @keydown.esc="cancelEditComment"
                      ></textarea>
                      <div class="flex gap-2">
                        <button
                          @click="saveEditComment"
                          class="px-3 py-1.5 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700 transition-colors"
                        >
                          Сохранить
                        </button>
                        <button
                          @click="cancelEditComment"
                          class="px-3 py-1.5 bg-neutral-200 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 text-sm rounded-lg hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors"
                        >
                          Отмена
                        </button>
                      </div>
                    </div>
                    
                    <!-- View Mode -->
                    <p v-else class="text-sm text-neutral-700 dark:text-neutral-300 whitespace-pre-wrap">{{ comment.text }}</p>
                  </div>
                </div>
              </div>

              <!-- Comment Input -->
              <div class="p-4 border-t border-neutral-200 dark:border-neutral-700 shrink-0">
                <div class="flex gap-3">
                  <input
                    v-model="newComment"
                    type="text"
                    class="flex-1 px-4 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-600
                           bg-white dark:bg-neutral-900
                           text-neutral-900 dark:text-white
                           placeholder-neutral-400
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent
                           transition-all text-sm"
                    placeholder="Написать комментарий..."
                    @keydown.enter="submitComment"
                  />
                  <button
                    class="px-4 py-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 
                           disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    :disabled="!newComment.trim()"
                    @click="submitComment"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Usage Tab -->
            <div v-if="activeTab === 'usage'" class="p-5 space-y-6">
              <!-- Stats Grid -->
              <div class="grid grid-cols-2 gap-3">
                <div class="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-700/50">
                  <p class="text-2xl font-bold text-neutral-900 dark:text-white">{{ usage?.views || 0 }}</p>
                  <p class="text-xs text-neutral-500 dark:text-neutral-400">Просмотров</p>
                </div>
                <div class="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-700/50">
                  <p class="text-2xl font-bold text-neutral-900 dark:text-white">{{ usage?.downloads || 0 }}</p>
                  <p class="text-xs text-neutral-500 dark:text-neutral-400">Скачиваний</p>
                </div>
                <div class="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-700/50">
                  <p class="text-2xl font-bold text-neutral-900 dark:text-white">{{ usage?.shares || 0 }}</p>
                  <p class="text-xs text-neutral-500 dark:text-neutral-400">Поделились</p>
                </div>
                <div class="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-700/50">
                  <p class="text-2xl font-bold text-neutral-900 dark:text-white">{{ usage?.usedInLinks || 0 }}</p>
                  <p class="text-xs text-neutral-500 dark:text-neutral-400">В ссылках</p>
                </div>
              </div>

              <!-- Usage Details -->
              <section>
                <h3 class="text-sm font-semibold text-neutral-900 dark:text-white mb-3">Использование</h3>
                <ul class="space-y-2">
                  <li v-if="usage?.usedInLinks" class="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                    <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    Используется в {{ usage.usedInLinks }} публичных ссылках
                  </li>
                  <li v-if="usage?.usedInPublications" class="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                    <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                    Включен в {{ usage.usedInPublications }} публикации
                  </li>
                  <li v-if="usage?.lastViewedAt" class="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                    <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    Последний просмотр: {{ formatRelativeTime(usage.lastViewedAt) }}
                  </li>
                  <li v-if="usage?.lastDownloadedAt" class="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                    <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Последнее скачивание: {{ formatRelativeTime(usage.lastDownloadedAt) }}
                  </li>
                </ul>
              </section>
            </div>
          </div>
        </aside>
      </div>

      <!-- Media Editor Modal -->
      <MediaEditorModal
        :is-open="showMediaEditor"
        :asset="asset"
        :document-file="selectedDocumentFile"
        @close="showMediaEditor = false"
        @save-version="handleSaveAsVersion"
        @save-copy="handleSaveAsCopy"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Menu, MenuButton, MenuItem, MenuItems, Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import {
  ArrowDownTrayIcon,
  ArrowPathRoundedSquareIcon,
  ChevronDownIcon,
  DocumentIcon,
  DocumentTextIcon,
  PhotoIcon,
  ShareIcon,
  PencilSquareIcon
} from '@heroicons/vue/24/outline'
import { useAssetStore } from '@/stores/assetStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useAuthStore } from '@/stores/authStore'
import { apiService } from '@/services/apiService'
import { commentService } from '@/services/commentService'
import { resolveAssetImageUrl } from '@/utils/imageUtils'
import MetadataEditor from '@/components/asset/MetadataEditor.vue'
import WorkflowWidget from '@/components/asset/WorkflowWidget.vue'
import AIInsightsWidget from '@/components/asset/AIInsightsWidget.vue'
import MediaEditorModal from '@/components/asset/MediaEditorModal.vue'
import type { Asset, Comment, Version, ExtendedAsset, UsageStats, AIAnalysis } from '@/types/api'
import type { WorkflowState } from '@/mocks/workflows'

const route = useRoute()
const assetStore = useAssetStore()
const notificationStore = useNotificationStore()
const favoritesStore = useFavoritesStore()
const authStore = useAuthStore()

// State
const isLoading = ref(true)
const error = ref<string | null>(null)
const asset = ref<Asset | null>(null)
const extendedAsset = ref<ExtendedAsset | null>(null)
const activeTab = ref<'info' | 'metadata' | 'versions' | 'comments' | 'usage'>('info')
const zoom = ref(1)
const rotation = ref(0)
const newComment = ref('')
const showMediaEditor = ref(false)
const comments = ref<Comment[]>([])
const isLoadingComments = ref(false)
const editingCommentId = ref<number | null>(null)
const editingCommentText = ref('')
const collapsedSections = ref({
  exif: false,
  tags: false,
  ai: false,
  status: false
})

// Document files (real "versions" in Mayan are represented by DocumentFile list)
const documentFiles = ref<any[]>([])
const selectedDocumentFileId = ref<number | null>(null)
const newVersionFileInput = ref<HTMLInputElement | null>(null)

const selectedDocumentFile = computed(() => {
  const files = documentFiles.value || []
  if (!files.length) return null
  const id = selectedDocumentFileId.value ?? files[0]?.id
  return files.find((f: any) => Number(f?.id) === Number(id)) || files[0] || null
})

onMounted(() => {
  const isMobile = window.innerWidth < 768
  if (isMobile) {
    collapsedSections.value = {
      exif: true,
      tags: true,
      ai: true,
      status: true
    }
  }
})

const tabs = [
  { id: 'info', label: 'Инфо' },
  { id: 'metadata', label: 'Метаданные' },
  { id: 'versions', label: 'Версии' },
  { id: 'comments', label: 'Коммент.' },
  { id: 'usage', label: 'Стат.' },
] as const

// Computed
const assetId = computed(() => Number(route.params.id))

const fileExtension = computed(() => {
  const name = asset.value?.file_details?.filename || asset.value?.filename || asset.value?.label || ''
  const match = name.match(/\.([a-z0-9]+)$/i)
  return match ? match[1].toLowerCase() : ''
})

const isImage = computed(() => {
  if (asset.value?.mime_type?.startsWith('image/')) return true
  // Fallback: if we have preview/thumbnail, treat as image to render
  return !!(asset.value?.preview_url || asset.value?.thumbnail_url)
})
const isVideo = computed(() => asset.value?.mime_type?.startsWith('video/'))
const isDocument = computed(() => 
  asset.value?.mime_type?.includes('pdf') || 
  asset.value?.mime_type?.includes('document') ||
  asset.value?.mime_type?.includes('word')
)
const isAudio = computed(() => asset.value?.mime_type?.startsWith('audio/'))

const hasPreviewUrl = computed(() => !!(asset.value?.preview_url || asset.value?.thumbnail_url))
// When user selects a specific document file version, we use these refs
// to override the main preview image with that version's first page.
const previewOverride = ref<string | null>(null)
const previewOverrideObjectUrl = ref<string | null>(null)

// IMPORTANT: do not break the current preview pipeline.
// If a user selects a specific document file version, we set `previewOverride`,
// which should force the preview area to render even for non-image MIME types.
const showPreview = computed(() => {
  if (previewOverride.value || previewFallback.value) return true
  return isImage.value || (hasPreviewUrl.value && !isVideo.value)
})

const documentType = computed(() => {
  if (isImage.value) return 'image'
  if (isVideo.value) return 'video'
  if (isDocument.value) return 'document'
  if (isAudio.value) return 'audio'
  return 'image' // default
})

// Versions UI should reflect Mayan document files (multiple files per document).
// Keep the UI shape similar to Version[] used by the template.
const versions = computed((): any[] => {
  const files = documentFiles.value || []
  if (!files.length) return []

  const currentId = selectedDocumentFileId.value
  return files.map((f: any) => {
    return {
      id: f.id,
      filename: f.filename,
      uploaded_by: 'Система',
      uploaded_date: f.timestamp,
      is_current: currentId ? f.id === currentId : false,
      size: f.size,
      _file: f,
    }
  })
})

// Comments are now loaded from API, not from asset

const usage = computed((): UsageStats | undefined => {
  return extendedAsset.value?.usage
})

const previewSrc = computed(() => resolveAssetImageUrl(asset.value))
// When user selects a specific document file version, we override the preview src.
const previewOverride = ref<string | null>(null)
// Track object URL to revoke and avoid memory leaks.
const previewOverrideObjectUrl = ref<string | null>(null)
const previewFallback = ref<string | null>(null)
const previewResolved = computed(() => previewOverride.value || previewFallback.value || previewSrc.value)
const isFavorite = computed(() => {
  if (!asset.value) return false
  return favoritesStore.isFavorite(asset.value.id) || asset.value.is_favorite === true || asset.value.isFavorite === true
})
const previewError = ref(false)

// Methods
async function loadAsset() {
  isLoading.value = true
  error.value = null
  previewError.value = false

  try {
    console.log('[AssetDetail] Loading asset:', assetId.value)

    // Always force reload to get fresh file data
    const storeAsset = await assetStore.getAssetDetail(assetId.value, true)
    
    if (storeAsset) {
      console.log('[AssetDetail] Loaded from real API:', storeAsset)
      asset.value = storeAsset as Asset
      
      // If asset has AI analysis, set it as extended data
      if (storeAsset.ai_analysis) {
        extendedAsset.value = {
          ...storeAsset,
          ai_analysis: storeAsset.ai_analysis
        } as ExtendedAsset
      } else {
        extendedAsset.value = storeAsset as ExtendedAsset
      }
    } else {
      error.value = `Актив с ID ${assetId.value} не найден`
    }

    // Load all document files (versions) for sidebar "История версий"
    // IMPORTANT: always use numeric route id as fallback, since some adapters can
    // temporarily return partial asset objects.
    const documentId = Number(asset.value?.id || assetId.value)
    if (Number.isFinite(documentId) && documentId > 0) {
      try {
        const filesResponse: any = await apiService.get(
          `/api/v4/documents/${documentId}/files/`,
          { params: { page_size: 200 } } as any,
          false
        )
        const results = Array.isArray(filesResponse?.results)
          ? filesResponse.results
          : (Array.isArray(filesResponse) ? filesResponse : [])
        // Sort newest first
        documentFiles.value = results.sort(
          (a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        )

        // Default selected file: latest file id (if available), otherwise newest by timestamp
        const latestId = (asset.value as any)?.file_latest_id
        selectedDocumentFileId.value =
          typeof latestId === 'number'
            ? latestId
            : (documentFiles.value[0]?.id ?? null)

        // Do NOT override preview by default; keep existing preview logic.
        if (previewOverrideObjectUrl.value) {
          try {
            window.URL.revokeObjectURL(previewOverrideObjectUrl.value)
          } catch {
            // ignore
          }
          previewOverrideObjectUrl.value = null
        }
        previewOverride.value = null
      } catch (filesErr) {
        console.warn('[AssetDetail] Failed to load document files:', filesErr)
        documentFiles.value = []
        selectedDocumentFileId.value = null
      }
    }

  } catch (e: any) {
    console.error('[AssetDetail] Error loading asset:', e)
    error.value = e.message || 'Не удалось загрузить актив'
  } finally {
    isLoading.value = false
  }
}

function _toRelativeApiPath(url: string): string {
  try {
    const parsed = new URL(url)
    return `${parsed.pathname}${parsed.search}`
  } catch (e) {
    // Already relative
    return url
  }
}

async function handleSelectDocumentFile(file: any): Promise<void> {
  if (!file) return
  selectedDocumentFileId.value = file.id
  previewError.value = false
  previewFallback.value = null

  // Cleanup previous object URL, if any
  if (previewOverrideObjectUrl.value) {
    try {
      window.URL.revokeObjectURL(previewOverrideObjectUrl.value)
    } catch (e) {
      // ignore
    }
    previewOverrideObjectUrl.value = null
  }

  // Prefer API-provided first-page image URL.
  const imageUrl: string | null = file?.pages_first?.image_url || null
  if (!imageUrl) {
    previewOverride.value = null
    return
  }

  // IMPORTANT: Keep existing preview pipeline, but for selected versions
  // fetch the image as blob via apiService to include auth headers and
  // avoid <img> 401s. If this fails, fallback to direct URL.
  try {
    const relative = _toRelativeApiPath(imageUrl)
    const blob = await apiService.get<Blob>(
      relative,
      { responseType: 'blob' } as any,
      false
    )
    const objectUrl = window.URL.createObjectURL(blob)
    previewOverrideObjectUrl.value = objectUrl
    previewOverride.value = objectUrl
  } catch (e) {
    previewOverride.value = _toRelativeApiPath(imageUrl)
  }
}

async function toggleFavorite(): Promise<void> {
  if (!asset.value) return
  try {
    await favoritesStore.toggleFavorite(asset.value.id)
    asset.value.is_favorite = favoritesStore.isFavorite(asset.value.id)
  } catch (e) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка избранного',
      message: 'Не удалось обновить избранное'
    })
  }
}

function handlePreviewImageError(): void {
  // First failure: try placeholder
  if (!previewFallback.value) {
    // If override is invalid, clear it so we can fall back.
    if (previewOverrideObjectUrl.value) {
      try {
        URL.revokeObjectURL(previewOverrideObjectUrl.value)
      } catch {
        // ignore
      }
      previewOverrideObjectUrl.value = null
    }
    previewOverride.value = null
    previewFallback.value = '/assets/placeholder.png'
    previewError.value = false
    return
  }
  previewError.value = true
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatDate(dateString: string | undefined): string {
  if (!dateString) return '--'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '--'
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'только что'
  if (diffMins < 60) return `${diffMins} мин. назад`
  if (diffHours < 24) return `${diffHours} ч. назад`
  if (diffDays < 7) return `${diffDays} дн. назад`
  return formatDate(dateString)
}

function formatDuration(seconds?: number): string {
  if (!seconds) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function zoomIn() {
  if (zoom.value < 3) zoom.value = Math.min(3, zoom.value + 0.25)
}

function zoomOut() {
  if (zoom.value > 0.5) zoom.value = Math.max(0.5, zoom.value - 0.25)
}

function rotateLeft() {
  rotation.value = (rotation.value - 90) % 360
}

function resetView() {
  zoom.value = 1
  rotation.value = 0
}

function scrollToTop() {
  const container = document.querySelector('.asset-detail-page') as HTMLElement | null
  if (container) {
    container.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

async function handleDownload() {
  if (!asset.value) return

  const filename =
    asset.value.file_details?.filename ||
    asset.value.filename ||
    asset.value.label ||
    `document-${asset.value.id}`

  notificationStore.addNotification({
    type: 'info',
    title: 'Загрузка началась',
    message: `Скачивание ${filename}...`,
  })

  // Handle async download
  const performDownload = async () => {
    try {
      // Prefer selected document file download URL (when user picked a version)
      const selectedFile = selectedDocumentFileId.value
        ? documentFiles.value.find((f: any) => f.id === selectedDocumentFileId.value)
        : null

      let downloadUrl = selectedFile?.download_url || asset.value.download_url

      // If no download_url, try to get file ID first
      if (!downloadUrl) {
        let fileId = selectedFile?.id || asset.value.file_latest_id

        // If no file_latest_id, fetch file list to get latest file ID
        if (!fileId) {
          try {
            const filesResponse = await apiService.get(`/api/v4/documents/${asset.value.id}/files/`)
            if (filesResponse.results && filesResponse.results.length > 0) {
              // Sort by timestamp descending and take the latest
              const latestFile = filesResponse.results
                .sort((a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0]
              fileId = latestFile.id
            }
          } catch (fileError) {
            console.warn('[AssetDetail] Could not fetch file list:', fileError)
          }
        }

        // Construct download URL with file ID
        if (fileId) {
          downloadUrl = `/api/v4/documents/${asset.value.id}/files/${fileId}/download/`
        }
      }

      if (!downloadUrl) {
        throw new Error('Could not determine download URL')
      }

      // Fetch blob via API to avoid SPA HTML fallback and include auth headers
      const blob = await apiService.get<Blob>(downloadUrl, {
        responseType: 'blob'
      } as any)

      const objectUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = objectUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(objectUrl)
    } catch (err) {
      console.error('[AssetDetail] Download failed', err)
      notificationStore.addNotification({
        type: 'error',
        title: 'Ошибка загрузки',
        message: 'Не удалось скачать файл'
      })
    }
  }

  performDownload()
}

type DownloadFormat = 'original' | 'low_res' | 'high_res' | 'pdf'

function handleDownloadAs(format: DownloadFormat) {
  if (!asset.value) return
  
  const formatLabels: Record<DownloadFormat, string> = {
    original: 'Оригинал',
    low_res: 'Low Res (JPG, 72dpi)',
    high_res: 'High Res (PNG, 300dpi)',
    pdf: 'PDF'
  }
  
  notificationStore.addNotification({
    type: 'info',
    title: 'Генерация файла',
    message: `Подготовка: ${formatLabels[format]}...`,
  })
  
  if (format === 'original') {
    handleDownload()
    return
  }

  // Map UI formats to backend target formats
  const targetFormat = format === 'pdf'
    ? 'pdf'
    : format === 'high_res'
      ? 'png'
      : 'jpeg' // low_res default

  // Handle async conversion
  const performConversion = async () => {
    try {
      const blob = await apiService.get<Blob>(
        `/api/v4/headless/documents/${asset.value.id}/convert/`,
        {
          params: { format: targetFormat },
          responseType: 'blob'
        } as any
      )

      const objectUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      const baseName =
        asset.value.file_details?.filename?.split('.')?.[0] ||
        asset.value.filename?.split('.')?.[0] ||
        asset.value.label ||
        `document-${asset.value.id}`
      link.href = objectUrl
      link.download = `${baseName}.${targetFormat === 'jpeg' ? 'jpg' : targetFormat}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(objectUrl)

      notificationStore.addNotification({
        type: 'success',
        title: 'Готово',
        message: `Файл скачан в формате ${formatLabels[format]}`
      })
    } catch (err) {
      console.error('[AssetDetail] Conversion download failed', err)
      notificationStore.addNotification({
        type: 'error',
        title: 'Ошибка конвертации',
        message: `Не удалось скачать файл в формате ${formatLabels[format]}`
      })
    }
  }

  performConversion()
}

function handleShare() {
  notificationStore.addNotification({
    type: 'info',
    title: 'Поделиться',
    message: 'Функция поделиться будет добавлена позже',
  })
}

function handleWorkflowStatusChange(newState: WorkflowState) {
  console.log('Workflow status changed to:', newState.label)
  
  // If status changed to "Approved", show the metadata tab
  // and maybe highlight the "Approval Data" section
  if (newState.id === 'approved') {
    activeTab.value = 'metadata'
  }
}

function handleMetadataSave(typeId: number) {
  console.log('Metadata saved for type:', typeId)
}

function handleTagsUpdated(tags: AITag[]) {
  console.log('Tags updated:', tags)
  // Could update the asset's tags here
  if (asset.value && tags.length > 0) {
    const newTags = tags.map(t => t.label)
    asset.value.tags = [...(asset.value.tags || []), ...newTags]
  }
}

function handleAnalysisComplete(analysis: AIAnalysis) {
  console.log('AI Analysis complete:', analysis)
  notificationStore.addNotification({
    type: 'success',
    title: 'AI анализ завершён',
    message: `Найдено ${analysis.tags.length} тегов`
  })
}

async function handleSaveAsVersion(_assetId: number, fileId: number) {
  const documentId = Number(asset.value?.id || assetId.value)
  if (!Number.isFinite(documentId) || documentId <= 0) {
    await loadAsset()
    return
  }

  activeTab.value = 'versions'
  const beforeCount = documentFiles.value?.length || 0

  notificationStore.addNotification({
    type: 'info',
    title: 'Версия в обработке',
    message: 'Файл сохранён, ожидаем появления версии в списке...'
  })

  const maxAttempts = 14
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    await new Promise((r) => setTimeout(r, 1500))
    try {
      const filesResponse: any = await apiService.get(
        `/api/v4/documents/${documentId}/files/`,
        { params: { page_size: 200 } } as any,
        false
      )
      const results = Array.isArray(filesResponse?.results)
        ? filesResponse.results
        : (Array.isArray(filesResponse) ? filesResponse : [])

      documentFiles.value = results.sort(
        (a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )

      const found = fileId
        ? documentFiles.value.find((f: any) => Number(f?.id) === Number(fileId))
        : null

      if (found || (documentFiles.value?.length || 0) > beforeCount) {
        const selected = found || documentFiles.value[0]
        selectedDocumentFileId.value = selected?.id ?? null
        if (selected) {
          await handleSelectDocumentFile(selected)
        }
        notificationStore.addNotification({
          type: 'success',
          title: 'Версия добавлена',
          message: 'Новая версия появилась в списке'
        })
        return
      }
    } catch {
      // ignore and keep polling
    }
  }

  // Fallback: reload full asset (keeps UI consistent even if processing is slow)
  await loadAsset()
  notificationStore.addNotification({
    type: 'warning',
    title: 'Версия ещё обрабатывается',
    message: 'Если версия не появилась — подождите несколько секунд и откройте вкладку «Версии» снова.'
  })
}

function handleSaveAsCopy(_originalId: number, newAssetId: number) {
  console.log('Saved as copy:', newAssetId)
  notificationStore.addNotification({
    type: 'success',
    title: 'Копия создана',
    message: `Новый актив добавлен в галерею (ID: ${newAssetId})`
  })
}

function handleUploadNewVersion() {
  newVersionFileInput.value?.click()
}

async function handleNewVersionFileSelected(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return

  const documentId = Number(asset.value?.id || assetId.value)
  if (!Number.isFinite(documentId) || documentId <= 0) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось определить документ для загрузки версии'
    })
    return
  }

  const beforeCount = documentFiles.value?.length || 0

  try {
    const formData = new FormData()
    formData.append('file_new', file, file.name)
    formData.append('action', '1') // Replace. Create a new version and use the new file pages.
    formData.append('filename', file.name)
    formData.append('comment', 'Uploaded via DAM UI')

    await apiService.post(
      `/api/v4/documents/${documentId}/files/`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } } as any
    )

    notificationStore.addNotification({
      type: 'info',
      title: 'Загрузка запущена',
      message: 'Новая версия обрабатывается. Сейчас обновим список версий...'
    })

    const maxAttempts = 12
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      await new Promise((r) => setTimeout(r, 1500))
      try {
        const filesResponse: any = await apiService.get(
          `/api/v4/documents/${documentId}/files/`,
          { params: { page_size: 200 } } as any,
          false
        )
        const results = Array.isArray(filesResponse?.results)
          ? filesResponse.results
          : (Array.isArray(filesResponse) ? filesResponse : [])
        documentFiles.value = results.sort(
          (a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        )

        if ((documentFiles.value?.length || 0) > beforeCount) {
          selectedDocumentFileId.value = documentFiles.value[0]?.id ?? null
          notificationStore.addNotification({
            type: 'success',
            title: 'Версия добавлена',
            message: 'Новая версия появилась в списке'
          })
          return
        }
      } catch {
        // ignore and keep polling
      }
    }

    notificationStore.addNotification({
      type: 'warning',
      title: 'Загрузка ещё выполняется',
      message: 'Версия ещё обрабатывается. Обновите список через несколько секунд.'
    })
  } catch (err: any) {
    const message =
      err?.response?.data?.detail ||
      err?.response?.data?.error ||
      err?.message ||
      'Не удалось загрузить новую версию'
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message
    })
  }
}

function handleRevertVersion(version: Version) {
  notificationStore.addNotification({
    type: 'success',
    title: 'Версия восстановлена',
    message: `Откат к версии ${version.filename}`,
  })
}

// Load comments from API
async function loadComments() {
  if (!asset.value?.id) return
  
  isLoadingComments.value = true
  try {
    const documentId = Number(asset.value.id)
    if (!Number.isFinite(documentId) || documentId <= 0) {
      console.warn('[AssetDetail] Invalid document ID for comments:', asset.value.id)
      return
    }
    
    comments.value = await commentService.getComments(documentId)
  } catch (err: any) {
    console.error('[AssetDetail] Failed to load comments:', err)
    
    const errorMessage = err?.response?.status === 403
      ? 'Нет прав доступа для просмотра комментариев'
      : err?.response?.status === 404
      ? 'Документ не найден'
      : 'Не удалось загрузить комментарии'
    
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка загрузки',
      message: errorMessage
    })
    
    comments.value = []
  } finally {
    isLoadingComments.value = false
  }
}

// Create new comment
async function submitComment() {
  if (!newComment.value.trim() || !asset.value?.id) return
  
  const documentId = Number(asset.value.id)
  if (!Number.isFinite(documentId) || documentId <= 0) {
    console.warn('[AssetDetail] Invalid document ID for comment creation:', asset.value.id)
    return
  }
  
  const commentText = newComment.value.trim()
  newComment.value = '' // Clear input immediately for better UX
  
  try {
    await commentService.createComment(documentId, commentText)
    await loadComments() // Reload comments to get the new one with proper data
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Комментарий добавлен',
      message: 'Ваш комментарий успешно опубликован',
    })
  } catch (err: any) {
    newComment.value = commentText // Restore text on error
    
    const errorMessage = err?.response?.status === 403
      ? 'Нет прав доступа для создания комментариев'
      : err?.response?.status === 400
      ? err?.response?.data?.text?.[0] || 'Неверный формат комментария'
      : 'Не удалось создать комментарий'
    
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: errorMessage
    })
  }
}

// Start editing a comment
function startEditComment(comment: Comment) {
  editingCommentId.value = comment.id
  editingCommentText.value = comment.text
}

// Save edited comment
async function saveEditComment() {
  if (!editingCommentId.value || !asset.value?.id) return
  
  const documentId = Number(asset.value.id)
  const commentId = editingCommentId.value
  const commentText = editingCommentText.value.trim()
  
  if (!commentText) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Комментарий не может быть пустым'
    })
    return
  }
  
  try {
    await commentService.updateComment(documentId, commentId, commentText)
    await loadComments() // Reload to get updated comment
    
    editingCommentId.value = null
    editingCommentText.value = ''
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Комментарий обновлен',
      message: 'Изменения сохранены'
    })
  } catch (err: any) {
    const errorMessage = err?.response?.status === 403
      ? 'Нет прав доступа для редактирования комментария'
      : err?.response?.status === 404
      ? 'Комментарий не найден'
      : err?.response?.status === 400
      ? err?.response?.data?.text?.[0] || 'Неверный формат комментария'
      : 'Не удалось обновить комментарий'
    
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: errorMessage
    })
  }
}

// Cancel editing
function cancelEditComment() {
  editingCommentId.value = null
  editingCommentText.value = ''
}

// Delete comment
async function deleteComment(commentId: number) {
  if (!asset.value?.id) return
  
  if (!confirm('Удалить комментарий? Это действие нельзя отменить.')) {
    return
  }
  
  const documentId = Number(asset.value.id)
  
  try {
    await commentService.deleteComment(documentId, commentId)
    await loadComments() // Reload to remove deleted comment
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Комментарий удален',
      message: 'Комментарий успешно удален'
    })
  } catch (err: any) {
    const errorMessage = err?.response?.status === 403
      ? 'Нет прав доступа для удаления комментария'
      : err?.response?.status === 404
      ? 'Комментарий не найден'
      : 'Не удалось удалить комментарий'
    
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: errorMessage
    })
  }
}

// Check if current user can edit comment
function canEditComment(comment: Comment): boolean {
  return comment.author_id === authStore.user?.id
}

// Check if current user can delete comment
function canDeleteComment(comment: Comment): boolean {
  return comment.author_id === authStore.user?.id
}

// Watch route changes
watch(() => route.params.id, () => {
  if (route.params.id) {
    loadAsset()
  }
})

// Watch active tab to load comments when comments tab is opened
watch(() => activeTab.value, (tab) => {
  if (tab === 'comments' && asset.value?.id) {
    loadComments()
  }
})

// Load on mount
onMounted(() => {
  loadAsset()
  // Load comments if comments tab is active
  if (activeTab.value === 'comments' && asset.value?.id) {
    loadComments()
  }
})
</script>
