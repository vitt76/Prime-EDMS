<template>
  <div class="publication-card">
    <Card>
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <!-- Header -->
          <div class="flex items-center gap-3 mb-3">
            <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-900">
              {{ publication.title }}
            </h3>
            <Badge :variant="statusVariant" size="sm">
              {{ statusLabel }}
            </Badge>
          </div>

          <!-- Description -->
          <p v-if="publication.description" class="text-sm text-neutral-600 dark:text-neutral-600 mb-3 line-clamp-2">
            {{ publication.description }}
          </p>

          <!-- Metadata -->
          <div class="flex flex-wrap items-center gap-4 text-xs text-neutral-600 dark:text-neutral-600 mb-3">
            <div class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{{ formatDate(publication.created_date) }}</span>
            </div>
            <div class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <span>{{ publication.created_by }}</span>
            </div>
            <div class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <span>{{ publication.assets.length }} активов</span>
            </div>
          </div>

          <!-- Channels -->
          <div v-if="publication.channels && publication.channels.length > 0" class="flex flex-wrap gap-2 mb-3">
            <Badge
              v-for="channel in publication.channels"
              :key="channel.id"
              variant="info"
              size="sm"
            >
              {{ channel.name }}
            </Badge>
          </div>

          <!-- Analytics -->
          <div v-if="publication.analytics" class="flex items-center gap-4 text-sm">
            <div class="flex items-center gap-1 text-neutral-600 dark:text-neutral-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
              <span>{{ publication.analytics.views }} просмотров</span>
            </div>
            <div class="flex items-center gap-1 text-neutral-600 dark:text-neutral-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              <span>{{ publication.analytics.downloads }} скачиваний</span>
            </div>
            <div class="flex items-center gap-1 text-neutral-600 dark:text-neutral-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.552 3.546a2 2 0 002.938-2.187l.546-2.59A4.998 4.998 0 0017 12c0-.482-.114-.938-.316-1.342m0 2.684L12.448 8.454a2 2 0 00-2.938-2.187l-.546 2.59A4.998 4.998 0 007 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684"
                />
              </svg>
              <span>{{ publication.analytics.shares }} репостов</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2 ml-4">
          <button
            class="p-2 text-neutral-600 dark:text-neutral-600 hover:text-primary-500 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-100 transition-colors"
            @click="$emit('preview')"
            aria-label="Предпросмотр"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          </button>
          <button
            class="p-2 text-neutral-600 dark:text-neutral-600 hover:text-primary-500 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-100 transition-colors"
            @click="$emit('edit')"
            aria-label="Редактировать"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </button>
          <button
            class="p-2 text-neutral-600 dark:text-neutral-600 hover:text-error rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-100 transition-colors"
            @click="$emit('delete')"
            aria-label="Удалить"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import type { Publication } from '@/types/api'
import { formatDate } from '@/utils/formatters'
import Card from '@/components/Common/Card.vue'
import Badge from '@/components/Common/Badge.vue'
import { computed } from 'vue'

interface Props {
  publication: Publication
}

const props = defineProps<Props>()

defineEmits<{
  preview: []
  edit: []
  delete: []
}>()

const statusVariant = computed(() => {
  const statusMap: Record<Publication['status'], 'success' | 'warning' | 'info' | 'error'> = {
    published: 'success',
    scheduled: 'warning',
    draft: 'info',
    archived: 'error'
  }
  return statusMap[props.publication.status] || 'info'
})

const statusLabel = computed(() => {
  const labelMap: Record<Publication['status'], string> = {
    published: 'Опубликовано',
    scheduled: 'Запланировано',
    draft: 'Черновик',
    archived: 'Архив'
  }
  return labelMap[props.publication.status] || props.publication.status
})
</script>

<style scoped>
.publication-card {
  margin-bottom: 1rem;
}
</style>

