<template>
  <div class="quick-actions-panel bg-white dark:bg-white rounded-lg shadow-sm border border-neutral-100 p-5">
    <h2 class="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
      <span class="text-xl">⚡</span> Быстрые действия
    </h2>

    <div class="flex flex-col gap-3">
      <!-- Action 1: Run AI -->
      <button
        @click="goToGalleryForAI"
        class="w-full text-left flex items-start gap-3 p-3 rounded-md hover:bg-neutral-50 transition-colors border border-transparent hover:border-neutral-100"
      >
        <span class="text-2xl leading-none">🚀</span>
        <div>
          <div class="font-medium text-neutral-900">Запустить AI-анализ</div>
          <div class="text-xs text-neutral-500">Найти активы без тегов</div>
        </div>
      </button>

      <!-- Action 2: Duplicates -->
      <button
        @click="goToDuplicates"
        class="w-full text-left flex items-start gap-3 p-3 rounded-md hover:bg-neutral-50 transition-colors border border-transparent hover:border-neutral-100"
      >
        <span class="text-2xl leading-none">🔍</span>
        <div>
          <div class="font-medium text-neutral-900">Найти дубликаты</div>
          <div class="text-xs text-neutral-500">Сэкономить место</div>
        </div>
      </button>

      <!-- Action 3: Favorites -->
      <button
        @click="goToFavorites"
        class="w-full text-left flex items-start gap-3 p-3 rounded-md hover:bg-neutral-50 transition-colors border border-transparent hover:border-neutral-100"
      >
        <span class="text-2xl leading-none">⭐</span>
        <div>
          <div class="font-medium text-neutral-900">Открыть избранное</div>
          <div class="text-xs text-neutral-500">Ваши любимые активы</div>
        </div>
      </button>

      <!-- Action 4: Saved Searches -->
      <button
        @click="goToSavedSearches"
        class="w-full text-left flex items-start gap-3 p-3 rounded-md hover:bg-neutral-50 transition-colors border border-transparent hover:border-neutral-100"
      >
        <span class="text-2xl leading-none">🔖</span>
        <div>
          <div class="font-medium text-neutral-900">Сохраненные поиски</div>
          <div class="text-xs text-neutral-500">Вернуться к работе</div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goToDuplicates() {
  router.push({ name: 'dam', query: { duplicates: 'true' } })
}

function goToSavedSearches() {
  router.push({ name: 'dam', hash: '#search' })
}

function goToGalleryForAI() {
  router.push({ name: 'dam', query: { status: 'untagged' } })
}

function goToFavorites() {
  router.push({ name: 'dam', query: { favorites_only: 'true' } })
}
</script>