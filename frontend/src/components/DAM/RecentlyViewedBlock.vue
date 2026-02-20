<template>
  <section
    class="recently-viewed-block rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-4"
    aria-labelledby="recently-viewed-heading"
  >
    <div class="flex items-center justify-between mb-3">
      <h2
        id="recently-viewed-heading"
        class="text-sm font-semibold text-neutral-800 dark:text-neutral-200"
      >
        Недавно просмотренные
      </h2>
      <router-link
        v-if="assets.length > 0"
        to="/dam/recent"
        class="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
        aria-label="Показать все недавно просмотренные"
      >
        Показать все
      </router-link>
    </div>

    <!-- Loading: skeleton row -->
    <div
      v-if="loading"
      class="flex gap-3 overflow-hidden"
      role="status"
      aria-label="Загрузка недавно просмотренных"
    >
      <div
        v-for="i in 6"
        :key="i"
        class="flex-shrink-0 w-24 rounded-lg overflow-hidden bg-neutral-200 dark:bg-neutral-700 animate-pulse"
      >
        <div class="w-24 h-24" />
        <div class="h-3 mt-2 mx-1 rounded bg-neutral-300 dark:bg-neutral-600 w-4/5" />
      </div>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="py-4 text-center text-sm text-neutral-500 dark:text-neutral-400"
    >
      {{ error }}
    </div>

    <!-- Empty -->
    <div
      v-else-if="assets.length === 0"
      class="py-6 text-center text-sm text-neutral-500 dark:text-neutral-400"
    >
      <p>Пока нет недавно просмотренных</p>
      <p class="mt-1">Откройте актив в галерее, и он появится здесь</p>
    </div>

    <!-- List: horizontal scroll -->
    <div
      v-else
      class="flex gap-3 overflow-x-auto pb-2 -mx-1 scrollbar-thin"
    >
      <button
        v-for="asset in assets"
        :key="asset.id"
        type="button"
        class="flex-shrink-0 w-24 text-left rounded-lg overflow-hidden border border-transparent hover:border-primary-300 dark:hover:border-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
        :aria-label="`Открыть: ${asset.label}`"
        @click="handleAssetClick(asset)"
      >
        <div class="w-24 h-24 bg-neutral-100 dark:bg-neutral-700 relative overflow-hidden">
          <AssetThumbnail
            :src="asset.thumbnail_url || undefined"
            :alt="asset.label"
            class="object-cover w-full h-full"
          />
        </div>
        <p class="mt-1.5 px-0.5 text-xs text-neutral-700 dark:text-neutral-300 truncate">
          {{ asset.label }}
        </p>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AssetThumbnail from './AssetThumbnail.vue'
import { getRecentlyViewed } from '@/services/recentlyViewedService'
import type { Asset } from '@/types/api'

const props = withDefaults(
  defineProps<{
    limit?: number
  }>(),
  { limit: 12 }
)

const router = useRouter()
const assets = ref<Asset[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await getRecentlyViewed({ limit: props.limit, days: 30 })
    assets.value = res.results
  } catch (e: unknown) {
    const msg = e && typeof e === 'object' && 'message' in e ? String((e as Error).message) : 'Ошибка загрузки'
    error.value = msg
    assets.value = []
  } finally {
    loading.value = false
  }
}

function handleAssetClick(asset: Asset) {
  router.push(`/dam/assets/${asset.id}`)
}

onMounted(() => {
  load()
})

defineExpose({
  refresh: load
})
</script>
