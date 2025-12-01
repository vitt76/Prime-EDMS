<template>
  <div class="data-table">
    <!-- Loading State -->
    <div v-if="isLoading" class="data-table__loading" role="status" aria-live="polite">
      <div
        v-for="i in 5"
        :key="i"
        class="data-table__skeleton-row"
        :aria-label="`Loading row ${i}`"
      />
    </div>

    <!-- Empty State -->
    <div
      v-else-if="items.length === 0"
      class="data-table__empty"
      role="status"
      aria-live="polite"
    >
      <p>{{ emptyStateText }}</p>
      <slot name="empty-action" />
    </div>

    <!-- Table -->
    <div v-else class="data-table__wrapper">
      <table
        class="data-table__table"
        role="table"
        :aria-label="ariaLabel || 'Data table'"
      >
        <thead>
          <tr>
            <!-- Checkbox (if selectable) -->
            <th
              v-if="selectable"
              class="data-table__cell data-table__cell--checkbox"
              scope="col"
            >
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate="someSelected"
                @change="toggleAllSelected"
                aria-label="Select all rows"
              />
            </th>

            <!-- Column Headers -->
            <th
              v-for="col in columns"
              :key="col.key"
              :class="[
                'data-table__cell',
                `data-table__cell--${col.align || 'left'}`
              ]"
              scope="col"
              role="columnheader"
              :aria-sort="getSortOrder(col.key)"
              @click="sortable && col.sortable !== false && handleSort(col.key)"
            >
              <button
                v-if="sortable && col.sortable !== false"
                class="data-table__sort-btn"
                :aria-label="`Sort by ${col.label}`"
                type="button"
              >
                {{ col.label }}
                <span
                  v-if="sortKey === col.key"
                  class="data-table__sort-icon"
                  :aria-label="`Sorted ${sortOrder === 'asc' ? 'ascending' : 'descending'}`"
                >
                  <svg
                    v-if="sortOrder === 'asc'"
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M5 15l7-7 7 7"
                    />
                  </svg>
                  <svg
                    v-else
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </span>
              </button>
              <span v-else>{{ col.label }}</span>
            </th>

            <!-- Actions Column -->
            <th
              v-if="$slots['row-actions']"
              class="data-table__cell data-table__cell--actions"
              scope="col"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in items"
            :key="getRowKeyValue(item, index)"
            :class="{ 'data-table__row--selected': isRowSelected(item) }"
          >
            <!-- Checkbox -->
            <td
              v-if="selectable"
              class="data-table__cell data-table__cell--checkbox"
            >
              <input
                type="checkbox"
                :value="getRowKeyValue(item, index)"
                :checked="isRowSelected(item)"
                @change="toggleRowSelected(item)"
                :aria-label="`Select row ${index + 1}`"
              />
            </td>

            <!-- Data Cells -->
            <td
              v-for="col in columns"
              :key="col.key"
              :class="[
                'data-table__cell',
                `data-table__cell--${col.align || 'left'}`
              ]"
            >
              <slot
                :name="`col-${col.key}`"
                :item="item"
                :value="getNestedValue(item, col.key)"
                :index="index"
              >
                {{ formatCellValue(getNestedValue(item, col.key), col.format) }}
              </slot>
            </td>

            <!-- Actions -->
            <td
              v-if="$slots['row-actions']"
              class="data-table__cell data-table__cell--actions"
            >
              <slot name="row-actions" :item="item" :index="index" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends Record<string, any>">
import { ref, computed } from 'vue'

export interface Column {
  key: string
  label: string
  align?: 'left' | 'center' | 'right'
  format?: 'date' | 'currency' | 'boolean' | 'number'
  sortable?: boolean
  width?: string | number
}

interface Props {
  items: T[]
  columns: Column[]
  isLoading?: boolean
  selectable?: boolean
  sortable?: boolean
  emptyStateText?: string
  ariaLabel?: string
  getRowKey?: (item: T, index: number) => string | number
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  selectable: false,
  sortable: false,
  emptyStateText: 'No data available',
  getRowKey: (item: T, index: number) => (item.id ?? index) as string | number
})

const emit = defineEmits<{
  select: [items: T[]]
  sort: [key: string, order: 'asc' | 'desc']
  'action-click': [action: string, item: T]
}>()

// State
const selectedItems = ref<T[]>([])
const sortKey = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')

// Computed
const allSelected = computed(() => {
  return (
    props.items.length > 0 &&
    selectedItems.value.length === props.items.length &&
    props.items.every((item) => selectedItems.value.includes(item))
  )
})

const someSelected = computed(() => {
  return (
    selectedItems.value.length > 0 &&
    selectedItems.value.length < props.items.length
  )
})

// Methods
const toggleAllSelected = (): void => {
  if (allSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = [...props.items]
  }
  emit('select', selectedItems.value)
}

const toggleRowSelected = (item: T): void => {
  const index = selectedItems.value.findIndex(
    (selected) => getRowKeyValue(selected, -1) === getRowKeyValue(item, -1)
  )
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(item)
  }
  emit('select', selectedItems.value)
}

const isRowSelected = (item: T): boolean => {
  return selectedItems.value.some(
    (selected) => getRowKeyValue(selected, -1) === getRowKeyValue(item, -1)
  )
}

const handleSort = (key: string): void => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  emit('sort', key, sortOrder.value)
}

const getSortOrder = (
  key: string
): 'ascending' | 'descending' | 'none' => {
  if (sortKey.value !== key) return 'none'
  return sortOrder.value === 'asc' ? 'ascending' : 'descending'
}

const getNestedValue = (obj: T, path: string): any => {
  return path.split('.').reduce((acc, part) => acc?.[part], obj)
}

const formatCellValue = (value: any, format?: string): string => {
  if (value === null || value === undefined) return '—'

  switch (format) {
    case 'date':
      return new Date(value).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    case 'currency':
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
      }).format(value)
    case 'boolean':
      return value ? 'Yes' : 'No'
    case 'number':
      return new Intl.NumberFormat('ru-RU').format(value)
    default:
      return String(value)
  }
}

const getRowKeyValue = (item: T, index: number): string | number => {
  return props.getRowKey(item, index)
}
</script>

<style scoped lang="css">
.data-table {
  width: 100%;
  border-radius: var(--radius-lg, 8px);
  background: var(--color-surface, #ffffff);
  overflow: hidden;
  border: 1px solid var(--color-border, #e5e7eb);
}

.data-table__wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

.data-table__wrapper::-webkit-scrollbar {
  height: 8px;
}

.data-table__wrapper::-webkit-scrollbar-track {
  background: var(--color-bg-1, #f9fafb);
}

.data-table__wrapper::-webkit-scrollbar-thumb {
  background: var(--color-border, #d1d5db);
  border-radius: 4px;
}

.data-table__wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary, #9ca3af);
}

.data-table__table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-base, 14px);
}

.data-table__table thead {
  background: var(--color-bg-1, #f9fafb);
  border-bottom: 2px solid var(--color-border, #e5e7eb);
}

.data-table__table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--color-text, #111827);
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table__table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  color: var(--color-text, #111827);
}

.data-table__table tbody tr {
  transition: background-color 150ms ease;
}

.data-table__table tbody tr:hover {
  background: rgba(0, 0, 0, 0.02);
}

.data-table__table tbody tr.data-table__row--selected {
  background: rgba(59, 130, 246, 0.05);
}

.data-table__cell {
  vertical-align: middle;
}

.data-table__cell--checkbox {
  width: 44px;
  text-align: center;
}

.data-table__cell--center {
  text-align: center;
}

.data-table__cell--right {
  text-align: right;
}

.data-table__cell--actions {
  width: 120px;
  text-align: right;
}

.data-table__sort-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  font-weight: 600;
  transition: color 150ms ease;
  width: 100%;
}

.data-table__sort-btn:hover {
  color: var(--color-primary, #3b82f6);
}

.data-table__sort-btn:focus-visible {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: 2px;
  border-radius: 2px;
}

.data-table__sort-icon {
  display: inline-flex;
  align-items: center;
  color: var(--color-primary, #3b82f6);
}

.data-table__empty {
  padding: 48px 24px;
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
}

.data-table__loading {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-table__skeleton-row {
  height: 48px;
  background: linear-gradient(
    90deg,
    var(--color-bg-1, #f3f4f6) 25%,
    rgba(0, 0, 0, 0.02) 50%,
    var(--color-bg-1, #f3f4f6) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .data-table__table th,
  .data-table__table td {
    padding: 8px 12px;
    font-size: var(--font-size-sm, 12px);
  }

  .data-table__sort-btn {
    flex-direction: column;
    gap: 2px;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .data-table__skeleton-row {
    animation: none;
    opacity: 0.5;
  }

  .data-table__table tbody tr {
    transition: none;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .data-table__table tbody tr:hover {
    background: rgba(0, 0, 0, 0.1);
  }

  .data-table__table tbody tr.data-table__row--selected {
    background: rgba(59, 130, 246, 0.2);
    border: 2px solid var(--color-primary, #3b82f6);
  }
}
</style>



