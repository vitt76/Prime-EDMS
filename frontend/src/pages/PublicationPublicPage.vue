// @ts-nocheck
<template>
  <main class="publication-public-page">
    <div class="publication-public-page__inner">
      <!-- Loading skeleton -->
      <section
        v-if="isLoading"
        class="publication-public-page__loading"
        role="status"
        aria-live="polite"
      >
        <div class="publication-public-page__loading-card" v-for="row in 2" :key="row">
          <div class="publication-public-page__loading-line publication-public-page__loading-line--title" />
          <div class="publication-public-page__loading-line publication-public-page__loading-line--subtitle" />
          <div class="publication-public-page__loading-grid">
            <div
              class="publication-public-page__loading-square"
              v-for="cell in 4"
              :key="`cell-${row}-${cell}`"
            />
          </div>
        </div>
      </section>

      <!-- Error state -->
      <section
        v-else-if="error"
        class="publication-public-page__error"
        role="alert"
        aria-live="assertive"
      >
        <p class="publication-public-page__error-title">Access denied</p>
        <p class="publication-public-page__error-message">{{ error }}</p>
        <p class="publication-public-page__error-hint">
          Please verify the link or contact the publisher if the token is invalid or expired.
        </p>
      </section>

      <!-- Publication content -->
      <section v-else class="publication-public-page__content">
        <header class="publication-public-page__hero">
          <div class="publication-public-page__hero-copy">
            <p class="publication-public-page__eyebrow">Public link</p>
            <h1 class="publication-public-page__title">{{ publication?.title }}</h1>
            <p v-if="publication?.description" class="publication-public-page__description">
              {{ publication?.description }}
            </p>
            <div class="publication-public-page__hero-stats">
              <div>
                <span class="label">Views</span>
                <span class="value">{{ stats.views }}</span>
              </div>
              <div>
                <span class="label">Downloads</span>
                <span class="value">{{ stats.downloads }}</span>
              </div>
              <div v-if="publication?.status">
                <span class="label">Status</span>
                <span class="value">{{ publication.status }}</span>
              </div>
            </div>
          </div>
          <div
            v-if="heroThumbnail"
            class="publication-public-page__hero-thumbnail"
            :aria-label="`Preview for ${publication?.title}`"
          >
            <img
              :src="heroThumbnail"
              :alt="publication?.title || 'Publication preview'"
              loading="lazy"
              decoding="async"
            />
          </div>
        </header>

        <div class="publication-public-page__assets">
          <div class="publication-public-page__assets-header">
            <div>
              <p class="publication-public-page__assets-eyebrow">Assets</p>
              <h2 class="publication-public-page__assets-title">
                {{ assets.length }} file{{ assets.length === 1 ? '' : 's' }}
              </h2>
            </div>
            <p class="publication-public-page__assets-subtitle">
              Download-ready files optimized for fast delivery.
            </p>
          </div>

          <div v-if="assets.length" class="publication-public-page__grid">
            <article
              v-for="asset in assets"
              :key="asset.id"
              class="publication-public-page__asset-card"
            >
              <div class="publication-public-page__asset-media">
                <img
                  v-if="asset.thumbnail_url || asset.preview_url"
                  :src="asset.thumbnail_url || asset.preview_url"
                  :alt="asset.label || asset.filename || 'Asset preview'"
                  loading="lazy"
                  decoding="async"
                />
                <div v-else class="publication-public-page__asset-media-fallback">
                  <span>No preview</span>
                </div>
                <div class="publication-public-page__asset-overlay">
                  <span class="publication-public-page__asset-overlay-type">
                    {{ (asset.mime_type ?? 'file').split('/').pop()?.toUpperCase() || 'FILE' }}
                  </span>
                  <span class="publication-public-page__asset-overlay-size">
                    {{ formatBytes(asset.size) }}
                  </span>
                </div>
              </div>
              <div class="publication-public-page__asset-body">
                <h3>{{ asset.label || asset.filename }}</h3>
                <p class="publication-public-page__asset-meta">
                  {{ asset.mime_type || 'Unknown format' }} · {{ formatBytes(asset.size) }}
                </p>
                <Button
                  variant="primary"
                  size="sm"
                  type="button"
                  :disabled="!getAssetDownloadUrl(asset)"
                  @click="handleAssetDownload(asset)"
                >
                  Download
                </Button>
              </div>
            </article>
          </div>

          <div v-else class="publication-public-page__empty">
            <p>No files have been published yet. Check back later or contact the owner.</p>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
// @ts-nocheck
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Button from '@/components/Common/Button.vue'
import { distributionService } from '@/services/distributionService'
import type { Asset, Publication } from '@/types/api'

const route = useRoute()
const publication = ref<Publication | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)
const hasTrackedView = ref(false)

const token = computed(() => {
  const raw = route.params.token
  if (typeof raw === 'string') {
    return raw.trim()
  }
  if (Array.isArray(raw)) {
    return raw[0]?.trim() ?? ''
  }
  return ''
})

const assets = computed<Asset[]>(() => publication.value?.assets ?? [])

const stats = computed(() => ({
  views: publication.value?.analytics?.views ?? 0,
  downloads: publication.value?.analytics?.downloads ?? 0
}))

const heroThumbnail = computed(() => {
  const asset = publication.value?.assets?.[0]
  return asset?.thumbnail_url || asset?.preview_url || ''
})

const fetchPublication = async (): Promise<void> => {
  const publicToken = token.value
  if (!publicToken) {
    error.value = 'Invalid or missing access token.'
    publication.value = null
    isLoading.value = false
    return
  }

  isLoading.value = true
  error.value = null
  publication.value = null
  hasTrackedView.value = false

  try {
    publication.value = await distributionService.getPublicationByToken(publicToken)
    await trackView()
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unable to load the publication.'
    error.value = message || 'The token is invalid or has expired.'
  } finally {
    isLoading.value = false
  }
}

const trackView = async (): Promise<void> => {
  if (!token.value || hasTrackedView.value) {
    return
  }
  hasTrackedView.value = true

  try {
    await distributionService.trackPublicView(token.value)
  } catch {
    // no-op: analytics not critical
  }
}

const getAssetDownloadUrl = (asset: Asset): string | null => {
  return asset.download_url || asset.preview_url || asset.thumbnail_url || null
}

const handleAssetDownload = async (asset: Asset): Promise<void> => {
  const downloadUrl = getAssetDownloadUrl(asset)
  if (!downloadUrl) {
    return
  }

  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = asset.filename || asset.label || 'asset'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  if (!token.value) {
    return
  }

  try {
    await distributionService.trackPublicDownload(token.value, asset.id)
  } catch {
    // best effort
  }
}

const formatBytes = (value?: number): string => {
  if (!value || value <= 0) {
    return '—'
  }
  const units = ['B', 'KB', 'MB', 'GB']
  let index = 0
  let bytes = value
  while (bytes >= 1024 && index < units.length - 1) {
    bytes /= 1024
    index += 1
  }
  return `${bytes.toFixed(index === 0 ? 0 : 1)} ${units[index]}`
}

watch(
  token,
  () => {
    fetchPublication()
  },
  { immediate: true }
)
</script>

<style scoped>
:global(body) {
  background: var(--color-background);
}

.publication-public-page {
  min-height: 100vh;
  padding: 32px 16px 48px;
  display: flex;
  justify-content: center;
  background: linear-gradient(180deg, #f5f7fb 0%, #ffffff 100%);
}

.publication-public-page__inner {
  width: min(1200px, 100%);
}

.publication-public-page__loading,
.publication-public-page__error,
.publication-public-page__content {
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(16px);
}

.publication-public-page__loading-card + .publication-public-page__loading-card {
  margin-top: 24px;
}

.publication-public-page__loading-line {
  height: 14px;
  background: var(--color-bg-1);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
}

.publication-public-page__loading-line--title {
  width: 60%;
  height: 20px;
}

.publication-public-page__loading-line--subtitle {
  width: 40%;
}

.publication-public-page__loading-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 16px;
}

.publication-public-page__loading-square {
  height: 120px;
  background: var(--color-bg-1);
  border-radius: var(--radius-base);
}

.publication-public-page__error {
  text-align: center;
}

.publication-public-page__error-title {
  font-size: var(--font-size-2xl);
  margin-bottom: 8px;
}

.publication-public-page__error-message {
  font-weight: 600;
  margin-bottom: 4px;
}

.publication-public-page__error-hint {
  color: var(--color-text-secondary);
}

.publication-public-page__hero {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  align-items: center;
  margin-bottom: 32px;
}

.publication-public-page__hero-copy {
  flex: 1;
  min-width: 280px;
}

.publication-public-page__eyebrow {
  font-size: var(--font-size-sm);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.publication-public-page__title {
  margin: 0;
  font-size: var(--font-size-4xl);
  line-height: 1.2;
}

.publication-public-page__description {
  color: var(--color-text-secondary);
  margin-top: 12px;
  font-size: var(--font-size-base);
}

.publication-public-page__hero-stats {
  display: flex;
  gap: 24px;
  margin-top: 20px;
}

.publication-public-page__hero-stats .label {
  display: block;
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  text-transform: uppercase;
}

.publication-public-page__hero-stats .value {
  font-size: var(--font-size-2xl);
  font-weight: 600;
}

.publication-public-page__hero-thumbnail {
  width: min(250px, 35%);
  min-height: 150px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-bg-1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.publication-public-page__hero-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.publication-public-page__assets-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.publication-public-page__assets-eyebrow {
  font-size: var(--font-size-sm);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  margin: 0;
}

.publication-public-page__assets-title {
  margin: 4px 0 0;
  font-size: var(--font-size-3xl);
}

.publication-public-page__assets-subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.publication-public-page__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.publication-public-page__asset-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 320px;
}

.publication-public-page__asset-media {
  position: relative;
  height: 160px;
  background: var(--color-bg-1);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.publication-public-page__asset-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.publication-public-page__asset-media-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
}

.publication-public-page__asset-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 12px;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.7) 100%);
  color: #fff;
  font-size: var(--font-size-xs);
}

.publication-public-page__asset-overlay-type {
  font-weight: 700;
}

.publication-public-page__asset-overlay-size {
  align-self: flex-end;
}

.publication-public-page__asset-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.publication-public-page__asset-body h3 {
  margin: 0;
  font-size: var(--font-size-lg);
}

.publication-public-page__asset-meta {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.publication-public-page__empty {
  padding: 48px;
  background: var(--color-bg-1);
  border-radius: var(--radius-base);
  text-align: center;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .publication-public-page {
    padding: 24px 12px 32px;
  }

  .publication-public-page__loading-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }

  .publication-public-page__hero-stats {
    flex-direction: column;
    gap: 12px;
  }

  .publication-public-page__hero-thumbnail {
    width: 100%;
  }

  .publication-public-page__asset-card {
    min-height: 280px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .publication-public-page__asset-card,
  .publication-public-page__hero {
    transition: none;
  }
}
</style>

