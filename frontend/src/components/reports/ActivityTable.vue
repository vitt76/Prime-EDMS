<template>
  <div class="activity-table">
    <!-- Loading State -->
    <div v-if="isLoading" class="activity-table__loading" role="status" aria-live="polite">
      <div
        v-for="i in 5"
        :key="i"
        class="activity-table__skeleton-row"
        :aria-label="`Loading activity row ${i}`"
      />
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!isLoading && activities.length === 0"
      class="activity-table__empty"
      role="status"
      aria-live="polite"
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
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="activity-table__empty-text">No activity data available</p>
    </div>

    <!-- Activity Table -->
    <div v-else class="activity-table__wrapper">
      <table class="activity-table__table" role="table" aria-label="User activity log">
        <thead>
          <tr>
            <th class="activity-table__header" scope="col">User</th>
            <th class="activity-table__header" scope="col">Action</th>
            <th class="activity-table__header" scope="col">Asset</th>
            <th class="activity-table__header" scope="col">Time</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="activity in paginatedActivities"
            :key="`${activity.timestamp}-${activity.username}-${activity.asset_id || 'none'}`"
            class="activity-table__row"
          >
            <td class="activity-table__cell">
              <div class="activity-table__user">
                <span class="activity-table__username">{{ activity.username }}</span>
                <span class="activity-table__email">{{ activity.email }}</span>
              </div>
            </td>
            <td class="activity-table__cell">
              <span
                :class="['activity-table__badge', `activity-table__badge--${activity.action}`]"
              >
                {{ formatAction(activity.action) }}
              </span>
            </td>
            <td class="activity-table__cell">
              <span v-if="activity.asset_name" class="activity-table__asset">
                {{ activity.asset_name }}
              </span>
              <span v-else class="activity-table__asset--empty">—</span>
            </td>
            <td class="activity-table__cell">
              <time :datetime="activity.timestamp" class="activity-table__time">
                {{ formatTimestamp(activity.timestamp) }}
              </time>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div
        v-if="showPagination && totalPages > 1"
        class="activity-table__pagination"
        role="navigation"
        aria-label="Activity table pagination"
      >
        <Pagination
          :current-page="currentPage"
          :total-items="activities.length"
          :page-size="pageSize"
          @page-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { UserActivity } from '@/types/reports'
import Pagination from '@/components/Common/Pagination.vue'

interface Props {
  activities: UserActivity[]
  isLoading?: boolean
  pageSize?: number
  showPagination?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  pageSize: 10,
  showPagination: true
})

const currentPage = ref(1)

const paginatedActivities = computed(() => {
  if (!props.showPagination || props.activities.length <= props.pageSize) {
    return props.activities
  }
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return props.activities.slice(start, end)
})

const totalPages = computed(() => {
  if (!props.showPagination) return 1
  return Math.ceil(props.activities.length / props.pageSize)
})

const handlePageChange = (page: number): void => {
  currentPage.value = page
  // Scroll to top of table
  const tableWrapper = document.querySelector('.activity-table__wrapper')
  if (tableWrapper) {
    tableWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const formatAction = (action: UserActivity['action']): string => {
  const actionLabels: Record<UserActivity['action'], string> = {
    upload: 'Upload',
    download: 'Download',
    view: 'View',
    delete: 'Delete',
    share: 'Share',
    edit: 'Edit',
    comment: 'Comment',
    tag: 'Tag'
  }
  return actionLabels[action] || action
}

const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) {
    return 'Just now'
  } else if (diffMins < 60) {
    return `${diffMins}m ago`
  } else if (diffHours < 24) {
    return `${diffHours}h ago`
  } else if (diffDays < 7) {
    return `${diffDays}d ago`
  } else {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    })
  }
}
</script>

<style scoped lang="css">
.activity-table {
  width: 100%;
}

.activity-table__loading {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.activity-table__skeleton-row {
  height: 56px;
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

.activity-table__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: var(--color-text-secondary, #6b7280);
  gap: 12px;
}

.activity-table__empty-text {
  margin: 0;
  font-size: var(--font-size-base, 14px);
}

.activity-table__wrapper {
  overflow-x: auto;
  border-radius: var(--radius-base, 8px);
  border: 1px solid var(--color-border, #e5e7eb);
}

.activity-table__table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm, 12px);
}

.activity-table__header {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--color-text, #111827);
  background: var(--color-bg-1, #f9fafb);
  border-bottom: 2px solid var(--color-border, #e5e7eb);
  white-space: nowrap;
}

.activity-table__row {
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  transition: background-color 150ms ease;
}

.activity-table__row:hover {
  background: var(--color-bg-1, #f9fafb);
}

.activity-table__row:last-child {
  border-bottom: none;
}

.activity-table__cell {
  padding: 12px 16px;
  color: var(--color-text, #111827);
  vertical-align: middle;
}

.activity-table__user {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.activity-table__username {
  font-weight: 500;
  color: var(--color-text, #111827);
}

.activity-table__email {
  font-size: var(--font-size-xs, 11px);
  color: var(--color-text-secondary, #6b7280);
}

.activity-table__badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: var(--radius-sm, 4px);
  font-size: var(--font-size-xs, 11px);
  font-weight: 500;
  text-transform: capitalize;
}

.activity-table__badge--upload {
  background: rgba(16, 185, 129, 0.1);
  color: rgb(16, 185, 129);
}

.activity-table__badge--download {
  background: rgba(59, 130, 246, 0.1);
  color: rgb(59, 130, 246);
}

.activity-table__badge--view {
  background: rgba(139, 92, 246, 0.1);
  color: rgb(139, 92, 246);
}

.activity-table__badge--delete {
  background: rgba(239, 68, 68, 0.1);
  color: rgb(239, 68, 68);
}

.activity-table__badge--share {
  background: rgba(245, 158, 11, 0.1);
  color: rgb(245, 158, 11);
}

.activity-table__badge--edit {
  background: rgba(236, 72, 153, 0.1);
  color: rgb(236, 72, 153);
}

.activity-table__badge--comment {
  background: rgba(99, 102, 241, 0.1);
  color: rgb(99, 102, 241);
}

.activity-table__badge--tag {
  background: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
}

.activity-table__asset {
  color: var(--color-text, #111827);
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.activity-table__asset--empty {
  color: var(--color-text-secondary, #6b7280);
  font-style: italic;
}

.activity-table__time {
  color: var(--color-text-secondary, #6b7280);
  font-size: var(--font-size-xs, 11px);
}

/* Responsive */
@media (max-width: 768px) {
  .activity-table__wrapper {
    font-size: var(--font-size-xs, 11px);
  }

  .activity-table__header,
  .activity-table__cell {
    padding: 8px 12px;
  }

  .activity-table__asset {
    max-width: 150px;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .activity-table__row {
    transition: none;
  }

  .activity-table__skeleton-row {
    animation: none;
  }
}
</style>

