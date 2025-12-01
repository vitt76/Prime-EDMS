<template>
  <div class="admin-tabs">
    <!-- Desktop Tabs -->
    <nav
      class="admin-tabs__nav"
      role="tablist"
      aria-label="Administration Navigation"
    >
      <button
        v-for="(tab, index) in availableTabs"
        :key="tab.id"
        :ref="(el) => setTabRef(el, index)"
        :class="[
          'admin-tabs__tab',
          { 'admin-tabs__tab--active': currentTab === tab.id }
        ]"
        :aria-selected="currentTab === tab.id"
        :aria-controls="`panel-${tab.id}`"
        role="tab"
        type="button"
        tabindex="0"
        @click="handleTabClick(tab.id)"
        @keydown="(e) => handleKeydown(e, tab.id, index)"
      >
        <component
          :is="getTabIcon(tab.icon)"
          class="admin-tabs__icon"
          aria-hidden="true"
        />
        <span class="admin-tabs__label">{{ tab.label }}</span>
      </button>
    </nav>

    <!-- Mobile Dropdown -->
    <div class="admin-tabs__mobile">
      <select
        :value="currentTab"
        class="admin-tabs__select"
        aria-label="Select administration section"
        @change="handleSelectChange"
      >
        <option
          v-for="tab in availableTabs"
          :key="tab.id"
          :value="tab.id"
        >
          {{ tab.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'

// Types
interface Tab {
  id: string
  label: string
  icon: string
  requiresPermission?: string
}

// Props
defineProps<{
  currentTab: string
}>()

// Emits
const emit = defineEmits<{
  'tab-change': [tabName: string]
}>()

// Hooks
const authStore = useAuthStore()

// Refs for tab elements (for arrow key navigation)
const tabRefs = ref<(HTMLButtonElement | null)[]>([])

// Tabs configuration
const allTabs: Tab[] = [
  {
    id: 'users',
    label: 'Users',
    icon: 'users',
    requiresPermission: 'admin.user_manage'
  },
  {
    id: 'schemas',
    label: 'Metadata Schemas',
    icon: 'database',
    requiresPermission: 'admin.schema_manage'
  },
  {
    id: 'workflows',
    label: 'Workflows',
    icon: 'flow',
    requiresPermission: 'admin.workflow_manage'
  },
  {
    id: 'integrations',
    label: 'Integrations',
    icon: 'plug',
    requiresPermission: 'admin.integrations_manage'
  },
  {
    id: 'reports',
    label: 'Reports',
    icon: 'chart-bar',
    requiresPermission: 'admin.reports_view'
  }
]

// Computed
const availableTabs = computed(() =>
  allTabs.filter(
    (tab) =>
      !tab.requiresPermission ||
      authStore.hasPermission.value(tab.requiresPermission)
  )
)

// Icon components
const UsersIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  `
}

const DatabaseIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
    </svg>
  `
}

const FlowIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  `
}

const PlugIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 3a2.828 2.828 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
    </svg>
  `
}

const ChartBarIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  `
}

// Methods
const setTabRef = (el: HTMLButtonElement | null, index: number): void => {
  if (el) {
    tabRefs.value[index] = el
  }
}

const getTabIcon = (iconName: string) => {
  const icons: Record<string, any> = {
    users: UsersIcon,
    database: DatabaseIcon,
    flow: FlowIcon,
    plug: PlugIcon,
    'chart-bar': ChartBarIcon
  }
  return icons[iconName] || UsersIcon
}

const handleTabClick = (tabId: string): void => {
  emit('tab-change', tabId)
}

const handleKeydown = (
  event: KeyboardEvent,
  tabId: string,
  currentIndex: number
): void => {
  if (event.key === 'Enter' || event.key === ' ') {
    if (event.key === ' ') {
      event.preventDefault()
    }
    handleTabClick(tabId)
    return
  }

  const tabs = availableTabs.value
  if (tabs.length === 0) return

  let newIndex: number | null = null

  if (event.key === 'ArrowLeft') {
    newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1
  } else if (event.key === 'ArrowRight') {
    newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0
  }

  if (newIndex !== null && newIndex >= 0 && newIndex < tabs.length) {
    event.preventDefault()
    const newTab = tabs[newIndex]
    if (newTab) {
      emit('tab-change', newTab.id)
      // Focus the new tab button
      setTimeout(() => {
        const tabElement = tabRefs.value[newIndex!]
        if (tabElement) {
          tabElement.focus()
        }
      }, 0)
    }
  }
}

const handleSelectChange = (event: Event): void => {
  const target = event.target as HTMLSelectElement
  emit('tab-change', target.value)
}
</script>

<style scoped>
.admin-tabs {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background: var(--color-surface, #ffffff);
  margin-bottom: 1.5rem;
}

.admin-tabs__nav {
  display: flex;
  flex-direction: row;
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

.admin-tabs__nav::-webkit-scrollbar {
  height: 4px;
}

.admin-tabs__nav::-webkit-scrollbar-track {
  background: transparent;
}

.admin-tabs__nav::-webkit-scrollbar-thumb {
  background: var(--color-border, #e5e7eb);
  border-radius: 2px;
}

.admin-tabs__tab {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-bottom: 3px solid transparent;
  background: transparent;
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  transition: all 200ms ease;
  min-height: 44px;
  min-width: 44px;
}

.admin-tabs__tab:hover {
  color: var(--color-text, #111827);
  background: rgba(0, 0, 0, 0.02);
}

.admin-tabs__tab--active {
  color: var(--color-primary, #3b82f6);
  border-bottom-color: var(--color-primary, #3b82f6);
  background: rgba(59, 130, 246, 0.05);
}

.admin-tabs__tab:focus-visible {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: -2px;
  border-radius: 4px 4px 0 0;
}


.admin-tabs__label {
  display: inline-block;
}

.admin-tabs__mobile {
  display: none;
}

.admin-tabs__select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.375rem;
  background: var(--color-surface, #ffffff);
  color: var(--color-text, #111827);
  font-size: 0.875rem;
  cursor: pointer;
  min-height: 44px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3E%3C/svg%3E");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

.admin-tabs__select:focus {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: 2px;
}

/* Icon styles */
.admin-tabs__icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: currentColor;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-tabs__nav {
    display: none;
  }

  .admin-tabs__mobile {
    display: block;
    padding: 0.75rem 1rem;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .admin-tabs__tab {
    transition: none;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .admin-tabs__tab {
    border: 1px solid transparent;
  }

  .admin-tabs__tab--active {
    border: 1px solid var(--color-primary, #3b82f6);
  }
}
</style>

