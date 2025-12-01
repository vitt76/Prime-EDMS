<template>
  <div
    class="gallery-item-skeleton"
    :class="{
      'gallery-item-skeleton--list': viewMode === 'list',
      'gallery-item-skeleton--grid': viewMode === 'grid'
    }"
    role="presentation"
    aria-hidden="true"
  >
    <!-- Preview skeleton -->
    <div class="gallery-item-skeleton__preview">
      <div class="gallery-item-skeleton__image animate-pulse bg-neutral-200 dark:bg-neutral-700"></div>
    </div>

    <!-- Info skeleton -->
    <div class="gallery-item-skeleton__info">
      <!-- List mode: checkbox and filename -->
      <div v-if="viewMode === 'list'" class="gallery-item-skeleton__list-header">
        <div class="gallery-item-skeleton__checkbox animate-pulse bg-neutral-200 dark:bg-neutral-700"></div>
        <div class="gallery-item-skeleton__filename animate-pulse bg-neutral-200 dark:bg-neutral-700"></div>
      </div>

      <!-- Grid mode: filename -->
      <div
        v-else
        class="gallery-item-skeleton__filename animate-pulse bg-neutral-200 dark:bg-neutral-700"
      ></div>

      <!-- Metadata skeleton -->
      <div class="gallery-item-skeleton__metadata">
        <div class="gallery-item-skeleton__size animate-pulse bg-neutral-200 dark:bg-neutral-700"></div>
        <div class="gallery-item-skeleton__date animate-pulse bg-neutral-200 dark:bg-neutral-700"></div>
        <div class="gallery-item-skeleton__tags animate-pulse bg-neutral-200 dark:bg-neutral-700"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Gallery Item Skeleton Component
 *
 * Loading placeholder for gallery items in virtual scroller.
 * Matches the layout of GalleryItem for smooth loading transitions.
 */

// Props
defineProps<{
  viewMode: 'grid' | 'list'
  index: number
}>()
</script>

<style scoped>
.gallery-item-skeleton {
  @apply pointer-events-none;
  @apply bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700;
}

.gallery-item-skeleton--grid {
  @apply rounded-lg overflow-hidden;
}

.gallery-item-skeleton--list {
  @apply rounded-none border-b border-l-0 border-r-0 first:border-t;
}

.gallery-item-skeleton__preview {
  @apply relative overflow-hidden;
}

.gallery-item-skeleton--grid .gallery-item-skeleton__preview {
  @apply aspect-square;
}

.gallery-item-skeleton--list .gallery-item-skeleton__preview {
  @apply w-16 h-16 flex-shrink-0;
}

.gallery-item-skeleton__image {
  @apply w-full h-full;
}

.gallery-item-skeleton__info {
  @apply p-3;
}

.gallery-item-skeleton--list .gallery-item-skeleton__info {
  @apply flex-1 flex items-center space-x-3 p-4;
}

.gallery-item-skeleton__list-header {
  @apply flex items-center space-x-3 mb-2;
}

.gallery-item-skeleton__checkbox {
  @apply w-5 h-5 rounded;
}

.gallery-item-skeleton__filename {
  @apply rounded;
}

.gallery-item-skeleton--grid .gallery-item-skeleton__filename {
  @apply h-4 w-3/4 mb-2;
}

.gallery-item-skeleton--list .gallery-item-skeleton__filename {
  @apply h-5 flex-1;
}

.gallery-item-skeleton__metadata {
  @apply flex flex-wrap items-center gap-x-3 gap-y-1;
}

.gallery-item-skeleton--list .gallery-item-skeleton__metadata {
  @apply flex-col items-start gap-x-0 gap-y-2;
}

.gallery-item-skeleton__size {
  @apply h-3 w-12 rounded;
}

.gallery-item-skeleton__date {
  @apply h-3 w-16 rounded;
}

.gallery-item-skeleton__tags {
  @apply h-3 w-20 rounded;
}

/* Stagger animation for multiple skeletons */
.gallery-item-skeleton:nth-child(2) .animate-pulse {
  animation-delay: 0.1s;
}

.gallery-item-skeleton:nth-child(3) .animate-pulse {
  animation-delay: 0.2s;
}

.gallery-item-skeleton:nth-child(4) .animate-pulse {
  animation-delay: 0.3s;
}

.gallery-item-skeleton:nth-child(5) .animate-pulse {
  animation-delay: 0.4s;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .gallery-item-skeleton .animate-pulse {
    animation: none;
  }
}
</style>




