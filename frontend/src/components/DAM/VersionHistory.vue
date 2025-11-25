<template>
  <div class="version-history">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-900">
        История версий ({{ versions.length }})
      </h3>
    </div>

    <!-- Versions List -->
    <div v-if="versions.length > 0" class="space-y-2">
      <div
        v-for="(version, index) in versions"
        :key="version.id"
        :class="[
          'p-4 rounded-lg border transition-colors',
          version.is_current
            ? 'bg-primary-50 dark:bg-primary-50 border-primary-300 dark:border-primary-300'
            : 'bg-neutral-50 dark:bg-neutral-50 border-neutral-300 dark:border-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-100'
        ]"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-medium text-neutral-900 dark:text-neutral-900">
                {{ version.filename }}
              </span>
              <Badge
                v-if="version.is_current"
                variant="success"
                size="sm"
              >
                Текущая версия
              </Badge>
              <Badge
                v-else-if="index === 0"
                variant="info"
                size="sm"
              >
                Последняя
              </Badge>
            </div>
            <div class="text-sm text-neutral-600 dark:text-neutral-600 space-y-1">
              <div class="flex items-center gap-4">
                <span>{{ formatDate(version.uploaded_date) }}</span>
                <span v-if="version.uploaded_by">• {{ version.uploaded_by }}</span>
                <span>• {{ formatFileSize(version.size) }}</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 ml-4">
            <Button
              variant="outline"
              size="sm"
              @click="handleDownload(version)"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Скачать
            </Button>
            <Button
              v-if="!version.is_current && canRestore"
              variant="primary"
              size="sm"
              @click="handleRestore(version)"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Восстановить
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8 text-neutral-600 dark:text-neutral-600">
      <svg
        class="mx-auto h-12 w-12 mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p>История версий пуста</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-4">
      <div class="animate-spin h-6 w-6 mx-auto text-primary-500"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { assetService } from '@/services/assetService'
import type { Version } from '@/types/api'
import { formatDate, formatFileSize } from '@/utils/formatters'
import Button from '@/components/Common/Button.vue'
import Badge from '@/components/Common/Badge.vue'
import { useAuthStore } from '@/stores/authStore'

interface Props {
  assetId: number
  initialVersions?: Version[]
  canRestore?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canRestore: true
})

const emit = defineEmits<{
  'version-download': [version: Version]
  'version-restore': [version: Version]
}>()

const authStore = useAuthStore()
const versions = ref<Version[]>(props.initialVersions || [])
const isLoading = ref(false)

onMounted(async () => {
  if (!props.initialVersions) {
    await loadVersions()
  }
})

watch(() => props.initialVersions, (newVersions) => {
  if (newVersions) {
    versions.value = newVersions
  }
})

async function loadVersions() {
  isLoading.value = true
  try {
    // In real implementation, this would be a separate endpoint
    // For now, we'll get it from asset detail
    const asset = await assetService.getAsset(props.assetId)
    if (asset.version_history) {
      versions.value = asset.version_history
    }
  } catch (error) {
    console.error('Failed to load versions:', error)
  } finally {
    isLoading.value = false
  }
}

function handleDownload(version: Version) {
  if (version.download_url) {
    window.open(version.download_url, '_blank')
  } else {
    // Fallback: construct download URL
    const downloadUrl = `/api/v4/dam/assets/${props.assetId}/versions/${version.id}/download/`
    window.open(downloadUrl, '_blank')
  }
  emit('version-download', version)
}

async function handleRestore(version: Version) {
  if (!confirm(`Вы уверены, что хотите восстановить версию "${version.filename}"?`)) {
    return
  }

  try {
    if (version.restore_url) {
      // Use restore URL if available
      await fetch(version.restore_url, { method: 'POST' })
    } else {
      // Fallback: use asset service
      // This would need to be added to assetService
      await assetService.updateAsset(props.assetId, {
        version_id: version.id
      } as any)
    }

    // Reload versions to update current version
    await loadVersions()
    emit('version-restore', version)
    
    // TODO: Show success toast
  } catch (error) {
    console.error('Failed to restore version:', error)
    // TODO: Show error toast
  }
}
</script>

<style scoped>
.version-history {
  padding: 1rem;
}
</style>

