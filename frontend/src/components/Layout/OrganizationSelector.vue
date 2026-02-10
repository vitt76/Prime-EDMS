<template>
  <div v-if="orgStore.hasMultipleOrgs" class="relative" ref="dropdownRef">
    <!-- Trigger button -->
    <button
      type="button"
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg
             hover:bg-gray-100 transition-colors text-sm"
      :class="{ 'opacity-50 pointer-events-none': orgStore.isSwitching }"
      @click="toggleDropdown"
      @keydown.escape="closeDropdown"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
      aria-label="Выбрать организацию"
    >
      <!-- Loading spinner when switching -->
      <svg
        v-if="orgStore.isSwitching"
        class="w-4 h-4 animate-spin text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <!-- Color dot (when not loading) -->
      <span
        v-else
        class="w-2.5 h-2.5 rounded-full flex-shrink-0"
        :style="{ backgroundColor: currentColor }"
      />
      <!-- Org name -->
      <span class="text-gray-700 font-medium max-w-[140px] truncate">
        {{ currentName }}
      </span>
      <!-- Chevron -->
      <svg
        class="w-4 h-4 text-gray-400 transition-transform"
        :class="{ 'rotate-180': isOpen }"
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
    </button>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute left-0 mt-2 w-64 bg-white rounded-xl shadow-lg
               border border-gray-200 py-1.5 z-50"
        role="listbox"
        aria-label="Список организаций"
        @keydown.escape="closeDropdown"
        @keydown.down.prevent="focusNext"
        @keydown.up.prevent="focusPrev"
      >
        <div class="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Организации
        </div>
        <button
          v-for="(org, index) in orgStore.userOrganizations"
          :key="org.id"
          :ref="(el) => setItemRef(el as HTMLElement | null, index)"
          type="button"
          role="option"
          :aria-selected="org.id === orgStore.currentOrganization?.id"
          class="w-full flex items-center gap-3 px-3 py-2.5 text-sm
                 hover:bg-gray-50 transition-colors focus:outline-none
                 focus:bg-gray-100"
          :class="{
            'bg-indigo-50 text-indigo-700': org.id === orgStore.currentOrganization?.id,
            'text-gray-700': org.id !== orgStore.currentOrganization?.id,
          }"
          @click="selectOrg(org.id)"
          @keydown.enter.prevent="selectOrg(org.id)"
        >
          <!-- Color dot -->
          <span
            class="w-2.5 h-2.5 rounded-full flex-shrink-0"
            :style="{ backgroundColor: org.branding_color || '#3B82F6' }"
          />
          <!-- Name + role -->
          <div class="flex-1 text-left min-w-0">
            <div class="font-medium truncate">{{ org.name }}</div>
            <div class="text-xs text-gray-400">{{ roleLabel(org.role) }}</div>
          </div>
          <!-- Check mark for current -->
          <svg
            v-if="org.id === orgStore.currentOrganization?.id"
            class="w-4 h-4 text-indigo-600 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </button>

        <!-- Settings link -->
        <div class="border-t border-gray-100 mt-1.5 pt-1.5">
          <router-link
            v-if="orgStore.isAdmin"
            to="/settings/organization"
            class="flex items-center gap-3 px-3 py-2.5 text-sm text-gray-600
                   hover:bg-gray-50 transition-colors"
            @click="closeDropdown"
          >
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Настройки организации
          </router-link>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useOrganizationStore } from '@/stores/organizationStore'
import type { OrganizationRole } from '@/types/organization'

const orgStore = useOrganizationStore()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const focusedIndex = ref(-1)
const itemRefs: (HTMLElement | null)[] = []

const currentName = computed(
  () => orgStore.currentOrganization?.name ?? 'Организация'
)
const currentColor = computed(
  () => orgStore.currentOrganization?.branding_color ?? '#3B82F6'
)

function roleLabel(role: OrganizationRole): string {
  const labels: Record<OrganizationRole, string> = {
    owner: 'Владелец',
    admin: 'Администратор',
    member: 'Участник',
    viewer: 'Наблюдатель',
  }
  return labels[role] ?? role
}

function setItemRef(el: HTMLElement | null, index: number) {
  itemRefs[index] = el
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    focusedIndex.value = -1
  }
}

function closeDropdown() {
  isOpen.value = false
  focusedIndex.value = -1
}

function focusNext() {
  const max = orgStore.userOrganizations.length - 1
  focusedIndex.value = Math.min(focusedIndex.value + 1, max)
  nextTick(() => {
    itemRefs[focusedIndex.value]?.focus()
  })
}

function focusPrev() {
  focusedIndex.value = Math.max(focusedIndex.value - 1, 0)
  nextTick(() => {
    itemRefs[focusedIndex.value]?.focus()
  })
}

function selectOrg(orgId: string) {
  if (orgId !== orgStore.currentOrganization?.id) {
    orgStore.switchOrganization(orgId)
    // Reload page to refetch all data with new org context
    window.location.reload()
  }
  closeDropdown()
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && isOpen.value) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})
</script>
