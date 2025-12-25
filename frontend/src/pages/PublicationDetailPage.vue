<template>
  <div class="publication-detail-page">
    <!-- Loading State -->
    <div v-if="isLoading" class="publication-detail-page__loading" role="status" aria-live="polite">
      <div class="publication-detail-page__skeleton">
        <div class="publication-detail-page__skeleton-header" />
        <div class="publication-detail-page__skeleton-content" />
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error && !publication"
      class="publication-detail-page__error"
      role="alert"
    >
      <p class="publication-detail-page__error-message">{{ error }}</p>
      <Button variant="primary" @click="fetchPublication">
        Try Again
      </Button>
    </div>

    <!-- Publication Content -->
    <div v-else-if="publication" class="publication-detail-page__content">
      <!-- Header Section -->
      <div class="publication-detail-page__header">
        <!-- Back Button -->
        <div class="publication-detail-page__back">
          <Button
            variant="secondary"
            size="sm"
            @click="handleBack"
            aria-label="Go back"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back
          </Button>
        </div>

        <div class="publication-detail-page__header-main">
          <!-- Thumbnail -->
          <div class="publication-detail-page__thumbnail">
            <img
              v-if="thumbnailUrl"
              :src="thumbnailUrl"
              :alt="`${publication.title} thumbnail`"
              class="publication-detail-page__thumbnail-img"
            />
            <div
              v-else
              class="publication-detail-page__thumbnail-placeholder"
              aria-label="No thumbnail"
            >
              <svg
                class="w-12 h-12 text-neutral-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
          </div>

          <!-- Publication Info -->
          <div class="publication-detail-page__info">
            <h1 class="publication-detail-page__title">{{ publication.title || 'Untitled Publication' }}</h1>
            <p
              v-if="publication.description"
              class="publication-detail-page__description"
            >
              {{ publication.description }}
            </p>

            <!-- Metadata -->
            <div class="publication-detail-page__metadata">
              <div class="publication-detail-page__metadata-item">
                <span class="publication-detail-page__metadata-label">Status:</span>
                <Badge :variant="statusVariant">{{ statusLabel }}</Badge>
              </div>
              <div class="publication-detail-page__metadata-item">
                <span class="publication-detail-page__metadata-label">Created:</span>
                <span class="publication-detail-page__metadata-value">
                  {{ formatDate(publication.created_date) }}
                </span>
              </div>
              <div
                v-if="publication.updated_date"
                class="publication-detail-page__metadata-item"
              >
                <span class="publication-detail-page__metadata-label">Updated:</span>
                <span class="publication-detail-page__metadata-value">
                  {{ formatDate(publication.updated_date) }}
                </span>
              </div>
              <!-- Schedule Information -->
              <div
                v-if="publication.schedule"
                class="publication-detail-page__metadata-item"
              >
                <span class="publication-detail-page__metadata-label">Schedule:</span>
                <span class="publication-detail-page__metadata-value">
                  {{ formatSchedule(publication.schedule) }}
                </span>
              </div>
              <!-- Channels Display -->
              <div
                v-if="publication.channels && publication.channels.length > 0"
                class="publication-detail-page__metadata-item"
              >
                <span class="publication-detail-page__metadata-label">Channels:</span>
                <div class="publication-detail-page__channels">
                  <Badge
                    v-for="channel in publication.channels"
                    :key="channel.id"
                    :variant="channel.status === 'active' ? 'success' : 'info'"
                    size="sm"
                    class="publication-detail-page__channel-badge"
                  >
                    <svg
                      v-if="channel.icon"
                      class="w-4 h-4"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <use :href="`#icon-${channel.icon}`" />
                    </svg>
                    {{ channel.name }}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="publication-detail-page__actions">
          <Button
            variant="secondary"
            @click="handleShare"
            aria-label="Share publication"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
              />
            </svg>
            Share
          </Button>

          <Button
            v-if="canEdit"
            variant="secondary"
            @click="handleEdit"
            aria-label="Edit publication"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            Edit
          </Button>

          <Button
            v-if="canDelete"
            variant="danger"
            @click="showDeleteModal = true"
            aria-label="Delete publication"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
            Delete
          </Button>
        </div>
      </div>

      <!-- Metrics Section -->
      <Card class="publication-detail-page__metrics" variant="elevated">
        <template #header>
          <div class="publication-detail-page__metrics-header">
            <h2 class="publication-detail-page__metrics-title">Metrics</h2>
            <Button
              variant="secondary"
              size="sm"
              @click="handleViewAnalytics"
              aria-label="View full analytics"
            >
              View Full Analytics
            </Button>
          </div>
        </template>

        <div class="publication-detail-page__metrics-grid">
          <div class="publication-detail-page__metric">
            <span class="publication-detail-page__metric-label">Views</span>
            <span class="publication-detail-page__metric-value">
              {{ metrics.views || 0 }}
            </span>
          </div>
          <div class="publication-detail-page__metric">
            <span class="publication-detail-page__metric-label">Downloads</span>
            <span class="publication-detail-page__metric-value">
              {{ metrics.downloads || 0 }}
            </span>
          </div>
          <div class="publication-detail-page__metric">
            <span class="publication-detail-page__metric-label">Shares</span>
            <span class="publication-detail-page__metric-value">
              {{ metrics.shares || 0 }}
            </span>
          </div>
        </div>
      </Card>

      <!-- Assets Section -->
      <Card class="publication-detail-page__assets" variant="elevated">
        <template #header>
          <div class="publication-detail-page__assets-header">
            <h2 class="publication-detail-page__assets-title">
              Assets ({{ assets.length }})
            </h2>
            <Button
              v-if="assets.length > 0"
              variant="secondary"
              size="sm"
              @click="handleDownloadAll"
              aria-label="Download all assets"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download All
            </Button>
          </div>
        </template>

        <!-- Empty State -->
        <div
          v-if="assets.length === 0 && !isLoading"
          class="publication-detail-page__assets-empty"
          role="status"
        >
          <svg
            class="w-16 h-16 text-neutral-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p class="publication-detail-page__assets-empty-text">No assets in this publication</p>
        </div>

        <!-- Assets Grid -->
        <div
          v-else
          class="publication-detail-page__assets-grid"
          role="grid"
          aria-label="Publication assets"
        >
          <div
            v-for="asset in assets"
            :key="asset.id"
            class="publication-detail-page__asset-card"
            role="gridcell"
          >
            <div class="publication-detail-page__asset-thumbnail">
              <img
                v-if="asset.thumbnail_url"
                :src="asset.thumbnail_url"
                :alt="asset.label || asset.filename || 'Asset thumbnail'"
                class="publication-detail-page__asset-thumbnail-img"
                @click="handleAssetClick(asset.id)"
              />
              <div
                v-else
                class="publication-detail-page__asset-thumbnail-placeholder"
                @click="handleAssetClick(asset.id)"
              >
                <svg
                  class="w-8 h-8 text-neutral-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>

              <!-- Asset Actions Overlay -->
              <div class="publication-detail-page__asset-actions">
                <Button
                  variant="primary"
                  size="sm"
                  @click.stop="handleAssetDownload(asset.id)"
                  aria-label="Download asset"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                    />
                  </svg>
                </Button>
              </div>
            </div>

            <div class="publication-detail-page__asset-info">
              <h3
                class="publication-detail-page__asset-name"
                @click="handleAssetClick(asset.id)"
              >
                {{ asset.label || asset.filename || 'Unnamed Asset' }}
              </h3>
              <p
                v-if="asset.size"
                class="publication-detail-page__asset-size"
              >
                {{ formatBytes(asset.size) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Loading Assets -->
        <div
          v-if="isLoading"
          class="publication-detail-page__assets-loading"
          role="status"
          aria-live="polite"
        >
          <div
            v-for="i in 6"
            :key="i"
            class="publication-detail-page__assets-skeleton"
            :aria-label="`Loading asset ${i}`"
          />
        </div>
      </Card>
    </div>

    <!-- Delete Confirmation Modal -->
    <DeleteConfirmModal
      v-if="showDeleteModal"
      :title="`Delete publication: ${publication?.title}`"
      message="Are you sure you want to delete this publication? This action cannot be undone."
      @confirm="handleDelete"
      @cancel="showDeleteModal = false"
    />

    <!-- Share Links Modal -->
    <ShareLinksModal
      v-if="showShareLinksModal && publication"
      :publication-id="publication.id"
      :is-open="showShareLinksModal"
      :share-links="shareLinks"
      @close="showShareLinksModal = false"
      @link-created="handleShareLinkCreated"
      @link-deleted="handleShareLinkDeleted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useDistributionStore } from '@/stores/distributionStore'
import { useUIStore } from '@/stores/uiStore'
import { distributionService } from '@/services/distributionService'
import Card from '@/components/Common/Card.vue'
import Button from '@/components/Common/Button.vue'
import Badge from '@/components/Common/Badge.vue'
import DeleteConfirmModal from '@/components/admin/DeleteConfirmModal.vue'
import ShareLinksModal from '@/components/Distribution/ShareLinksModal.vue'
import type { Publication, ShareLink } from '@/types/api'

// Hooks
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const distributionStore = useDistributionStore()
const uiStore = useUIStore()

// State
const publication = ref<Publication | null>(null)
const shareLinks = ref<ShareLink[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)
const showDeleteModal = ref(false)
const showShareLinksModal = ref(false)

// Computed
const publicationId = computed(() => {
  const id = route.params.id
  if (typeof id === 'string') {
    const parsed = parseInt(id)
    return isNaN(parsed) ? 0 : parsed
  }
  if (Array.isArray(id) && id.length > 0) {
    const parsed = parseInt(id[0] || '0')
    return isNaN(parsed) ? 0 : parsed
  }
  return 0
})

const assets = computed(() => {
  return publication.value?.assets || []
})

const metrics = computed(() => {
  if (!publication.value?.analytics) {
    return {
      views: 0,
      downloads: 0,
      shares: 0
    }
  }
  const analytics = publication.value.analytics
  return {
    views: analytics?.views || 0,
    downloads: analytics?.downloads || 0,
    shares: analytics?.shares || 0
  }
})

const canEdit = computed(() => {
  if (!publication.value || !authStore.user) return false
  const isOwner = publication.value.created_by_id === authStore.user.id
  const hasPermission = authStore.hasPermission('distribution.publication_edit')
  return isOwner && hasPermission
})

const canDelete = computed(() => {
  if (!publication.value || !authStore.user) return false
  const isOwner = publication.value.created_by_id === authStore.user.id
  const hasPermission = authStore.hasPermission('distribution.publication_delete')
  return isOwner && hasPermission
})

const statusVariant = computed(() => {
  if (!publication.value) return 'info'
  switch (publication.value.status) {
    case 'published':
      return 'success'
    case 'scheduled':
      return 'info'
    case 'draft':
      return 'warning'
    case 'archived':
      return 'info'
    default:
      return 'info'
  }
})

const statusLabel = computed(() => {
  if (!publication.value) return 'Unknown'
  return publication.value.status.charAt(0).toUpperCase() + publication.value.status.slice(1)
})

const thumbnailUrl = computed(() => {
  if (!publication.value || !publication.value.assets || publication.value.assets.length === 0) {
    return null
  }
  // Get thumbnail from first asset
  const firstAsset = publication.value.assets[0]
  if (!firstAsset) return null
  return firstAsset.thumbnail_url || firstAsset.preview_url || null
})

// Methods
const fetchPublication = async (): Promise<void> => {
  if (isNaN(publicationId.value)) {
    error.value = 'Invalid publication ID'
    return
  }

  isLoading.value = true
  error.value = null

  try {
    // Fetch publication using distributionStore
    const pub = await distributionStore.getPublication(publicationId.value)
    publication.value = pub

    // Fetch analytics if not included
    if (!pub.analytics) {
      try {
        const analytics = await distributionService.getPublicationAnalytics(publicationId.value)
        if (publication.value) {
          publication.value.analytics = analytics
        }
      } catch (err) {
        // Silently fail analytics - not critical
        console.error('Failed to load analytics:', err)
      }
    }

    // Fetch share links
    await fetchShareLinks()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load publication'
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: error.value
    })
  } finally {
    isLoading.value = false
  }
}

const fetchShareLinks = async (): Promise<void> => {
  if (!publication.value) return

  try {
    const links = await distributionService.getShareLinks(publication.value.id)
    shareLinks.value = links
  } catch (err) {
    // Silently fail share links - not critical
    console.error('Failed to load share links:', err)
  }
}

const handleShare = async (): Promise<void> => {
  if (!publication.value) return

  // Show share links management modal
  showShareLinksModal.value = true
}

const handleShareLinkCreated = async (): Promise<void> => {
  await fetchShareLinks()
  uiStore.addNotification({
    type: 'success',
    title: 'Success',
    message: 'Share link created successfully'
  })
}

const handleShareLinkDeleted = async (): Promise<void> => {
  await fetchShareLinks()
  uiStore.addNotification({
    type: 'success',
    title: 'Success',
    message: 'Share link deleted successfully'
  })
}

const handleBack = (): void => {
  router.push({ name: 'distribution' })
}

const handleViewAnalytics = (): void => {
  if (!publication.value) return
  router.push({
    name: 'publication-analytics',
    params: { id: publication.value.id }
  })
}

const handleEdit = (): void => {
  if (!publication.value) return
  router.push({
    name: 'publication-edit',
    params: { id: publication.value.id }
  })
}

const handleDelete = async (): Promise<void> => {
  if (!publication.value) return

  try {
    await distributionStore.deletePublication(publication.value.id)

    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Publication deleted successfully'
    })

    router.push({ name: 'distribution' })
  } catch (err) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to delete publication'
    })
  } finally {
    showDeleteModal.value = false
  }
}

const handleAssetClick = (assetId: number): void => {
  router.push({
    name: 'asset-detail',
    params: { id: assetId }
  })
}

const handleAssetDownload = async (assetId: number): Promise<void> => {
  try {
    const asset = assets.value.find((a) => a.id === assetId)
    if (!asset) {
      uiStore.addNotification({
        type: 'error',
        title: 'Error',
        message: 'Asset not found'
      })
      return
    }

    // Use preview_url or construct download URL
    const downloadUrl = asset.preview_url || `/api/v4/assets/${asset.id}/download/`

    // Trigger download
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = asset.filename || asset.label || 'asset'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Download started'
    })
  } catch (err) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to download asset'
    })
  }
}

const handleDownloadAll = async (): Promise<void> => {
  if (assets.value.length === 0) return

  try {
    // Download all assets one by one
    for (const asset of assets.value) {
      const downloadUrl = asset.preview_url || `/api/v4/assets/${asset.id}/download/`
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = asset.filename || asset.label || 'asset'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      // Small delay to avoid browser blocking multiple downloads
      await new Promise((resolve) => setTimeout(resolve, 100))
    }

    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Downloads started'
    })
  } catch (err) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to download assets'
    })
  }
}

const formatSchedule = (schedule?: Publication['schedule']): string => {
  if (!schedule) return 'Not scheduled'
  if (!schedule.start_date && !schedule.end_date) return 'Not scheduled'
  
  const start = schedule.start_date ? formatDate(schedule.start_date) : 'No start date'
  const end = schedule.end_date ? formatDate(schedule.end_date) : 'No end date'
  return `${start} - ${end}`
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Lifecycle
onMounted(async () => {
  // Permission check
  if (!authStore.hasPermission('distribution.publication_view')) {
    router.push({
      name: 'forbidden',
      query: {
        returnTo: route.fullPath,
        requiredPermission: 'distribution.publication_view'
      }
    })
    return
  }

  await fetchPublication()
})
</script>

<style scoped lang="css">
.publication-detail-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--color-background, #f9fafb);
  min-height: 100vh;
}

/* Loading State */
.publication-detail-page__loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.publication-detail-page__skeleton {
  width: 100%;
  max-width: 1200px;
}

.publication-detail-page__skeleton-header {
  height: 200px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 8px);
  margin-bottom: 24px;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.publication-detail-page__skeleton-content {
  height: 400px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 8px);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Error State */
.publication-detail-page__error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 400px;
  padding: 48px;
  background: var(--color-surface, #ffffff);
  border-radius: var(--radius-base, 8px);
  border: 1px solid var(--color-border, #e5e7eb);
}

.publication-detail-page__error-message {
  margin: 0;
  font-size: var(--font-size-lg, 18px);
  color: var(--color-text, #111827);
  text-align: center;
}

/* Header Section */
.publication-detail-page__header {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--color-surface, #ffffff);
  border-radius: var(--radius-base, 8px);
  border: 1px solid var(--color-border, #e5e7eb);
}

.publication-detail-page__header-main {
  display: flex;
  gap: 24px;
}

.publication-detail-page__thumbnail {
  flex-shrink: 0;
  width: 200px;
  height: 200px;
  border-radius: var(--radius-base, 8px);
  overflow: hidden;
  background: var(--color-bg-1, #f9fafb);
}

.publication-detail-page__thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.publication-detail-page__thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-1, #f9fafb);
}

.publication-detail-page__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.publication-detail-page__title {
  margin: 0;
  font-size: var(--font-size-3xl, 30px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.publication-detail-page__description {
  margin: 0;
  font-size: var(--font-size-base, 14px);
  color: var(--color-text-secondary, #6b7280);
  line-height: 1.6;
}

.publication-detail-page__metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
}

.publication-detail-page__metadata-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.publication-detail-page__metadata-label {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  font-weight: 500;
}

.publication-detail-page__metadata-value {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text, #111827);
}

.publication-detail-page__channels {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.publication-detail-page__channel-badge {
  display: flex;
  align-items: center;
  gap: 4px;
}

.publication-detail-page__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Metrics Section */
.publication-detail-page__metrics {
  padding: 24px;
}

.publication-detail-page__metrics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.publication-detail-page__metrics-title {
  margin: 0;
  font-size: var(--font-size-xl, 20px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.publication-detail-page__metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 24px;
  margin-top: 16px;
}

.publication-detail-page__metric {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 8px);
}

.publication-detail-page__metric-label {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.publication-detail-page__metric-value {
  font-size: var(--font-size-2xl, 24px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

/* Assets Section */
.publication-detail-page__assets {
  padding: 24px;
}

.publication-detail-page__assets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.publication-detail-page__assets-title {
  margin: 0;
  font-size: var(--font-size-xl, 20px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.publication-detail-page__assets-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 64px 24px;
  color: var(--color-text-secondary, #6b7280);
}

.publication-detail-page__assets-empty-text {
  margin: 0;
  font-size: var(--font-size-base, 14px);
}

.publication-detail-page__assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.publication-detail-page__asset-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--color-surface, #ffffff);
  border-radius: var(--radius-base, 8px);
  overflow: hidden;
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.publication-detail-page__asset-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1));
}

.publication-detail-page__asset-thumbnail {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 8px);
  overflow: hidden;
}

.publication-detail-page__asset-thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
}

.publication-detail-page__asset-thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.publication-detail-page__asset-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 200ms ease;
}

.publication-detail-page__asset-card:hover .publication-detail-page__asset-actions {
  opacity: 1;
}

.publication-detail-page__asset-info {
  padding: 0 4px;
}

.publication-detail-page__asset-name {
  margin: 0 0 4px 0;
  font-size: var(--font-size-sm, 12px);
  font-weight: 500;
  color: var(--color-text, #111827);
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.publication-detail-page__asset-name:hover {
  color: var(--color-primary, #3b82f6);
}

.publication-detail-page__asset-size {
  margin: 0;
  font-size: var(--font-size-xs, 11px);
  color: var(--color-text-secondary, #6b7280);
}

.publication-detail-page__assets-loading {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.publication-detail-page__assets-skeleton {
  aspect-ratio: 1;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 8px);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Responsive */
@media (max-width: 1024px) {
  .publication-detail-page__header-main {
    flex-direction: column;
  }

  .publication-detail-page__thumbnail {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
}

@media (max-width: 768px) {
  .publication-detail-page {
    padding: 16px;
  }

  .publication-detail-page__header {
    padding: 16px;
  }

  .publication-detail-page__actions {
    flex-direction: column;
  }

  .publication-detail-page__actions > * {
    width: 100%;
  }

  .publication-detail-page__assets-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
  }

  .publication-detail-page__metrics-grid {
    grid-template-columns: 1fr;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .publication-detail-page__skeleton-header,
  .publication-detail-page__skeleton-content,
  .publication-detail-page__assets-skeleton {
    animation: none;
  }

  .publication-detail-page__asset-card {
    transition: none;
  }
}
</style>

