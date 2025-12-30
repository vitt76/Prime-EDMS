<template>
  <Card padding="lg">
    <!-- Mobile: single button + drawer -->
    <div class="md:hidden flex items-center justify-between gap-3">
      <div class="text-sm text-neutral-700">
        Фильтры
        <span class="text-neutral-500">
          · {{ filtersSummary }}
        </span>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          type="button"
          @click="mobileOpen = true"
        >
          Фильтры
        </button>
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          type="button"
          @click="clear"
        >
          Сбросить
        </button>
      </div>
    </div>

    <!-- Desktop: compact single row, auto-apply -->
    <div class="hidden md:flex items-end gap-4">
      <div class="min-w-[260px]">
        <div class="text-xs text-neutral-600 mb-2">Период</div>
        <DateRangePicker v-model="localDateRange" />
      </div>

      <div class="min-w-[220px]">
        <div class="text-xs text-neutral-600 mb-2">Тип файла</div>
        <select
          v-model="localAssetType"
          class="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm bg-white text-neutral-900"
        >
          <option :value="''">Все типы</option>
          <option value="images">Изображения</option>
          <option value="videos">Видео</option>
          <option value="documents">Документы</option>
          <option value="other">Другое</option>
        </select>
      </div>

      <div class="flex-1 min-w-[220px]">
        <div class="text-xs text-neutral-600 mb-2">Департамент</div>
        <input
          v-model="localDepartment"
          type="text"
          class="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm bg-white text-neutral-900"
          placeholder="Например: Маркетинг"
        />
      </div>

      <div class="flex items-center gap-2">
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          type="button"
          @click="clear"
        >
          Сбросить
        </button>
      </div>
    </div>
  </Card>

  <!-- Drawer -->
  <div v-if="mobileOpen" class="fixed inset-0 z-50 md:hidden">
    <div class="absolute inset-0 bg-black/40" @click="mobileOpen = false" />
    <div class="absolute inset-x-0 bottom-0 bg-white rounded-t-2xl border border-neutral-200 p-4">
      <div class="flex items-center justify-between gap-4">
        <div class="text-base font-semibold text-neutral-900">Фильтры</div>
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          type="button"
          @click="mobileOpen = false"
        >
          Закрыть
        </button>
      </div>

      <div class="mt-4 space-y-4">
        <div>
          <div class="text-xs text-neutral-600 mb-2">Период</div>
          <DateRangePicker v-model="localDateRange" />
        </div>

        <div>
          <div class="text-xs text-neutral-600 mb-2">Тип файла</div>
          <select
            v-model="localAssetType"
            class="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm bg-white text-neutral-900"
          >
            <option :value="''">Все типы</option>
            <option value="images">Изображения</option>
            <option value="videos">Видео</option>
            <option value="documents">Документы</option>
            <option value="other">Другое</option>
          </select>
        </div>

        <div>
          <div class="text-xs text-neutral-600 mb-2">Департамент</div>
          <input
            v-model="localDepartment"
            type="text"
            class="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm bg-white text-neutral-900"
            placeholder="Например: Маркетинг"
          />
        </div>
      </div>

      <div class="mt-5 flex items-center gap-2">
        <button
          class="flex-1 px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          type="button"
          @click="clear"
        >
          Сбросить
        </button>
        <button
          class="flex-1 px-3 py-2 text-sm rounded-md bg-primary-600 text-white hover:bg-primary-700"
          type="button"
          @click="applyAndClose"
        >
          Применить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import Card from '@/components/Common/Card.vue'
import DateRangePicker from '@/components/Common/DateRangePicker.vue'

const props = defineProps<{
  dateRange: [string, string] | null
  assetType: 'images' | 'videos' | 'documents' | 'other' | null
  department?: string | null
}>()

const emit = defineEmits<{
  apply: [
    payload: {
      dateRange: [string, string] | null
      assetType: 'images' | 'videos' | 'documents' | 'other' | null
      department: string | null
    }
  ]
  clear: []
}>()

const localDateRange = ref<[string, string] | null>(props.dateRange)
const localAssetType = ref<string>(props.assetType || '')
const localDepartment = ref<string>(props.department || '')
const mobileOpen = ref(false)

let autoApplyTimer: number | null = null
function scheduleAutoApply(): void {
  if (autoApplyTimer) {
    window.clearTimeout(autoApplyTimer)
  }
  autoApplyTimer = window.setTimeout(() => {
    apply()
  }, 300)
}

const filtersSummary = computed(() => {
  const parts: string[] = []
  if (localDateRange.value) parts.push('период')
  if (localAssetType.value) parts.push('тип')
  if ((localDepartment.value || '').trim()) parts.push('департамент')
  return parts.length ? parts.join(', ') : 'без ограничений'
})

watch(
  () => props.dateRange,
  (v) => {
    localDateRange.value = v
  }
)
watch(
  () => props.assetType,
  (v) => {
    localAssetType.value = v || ''
  }
)
watch(
  () => props.department,
  (v) => {
    localDepartment.value = v || ''
  }
)

watch(
  () => [localDateRange.value, localAssetType.value, localDepartment.value],
  () => {
    // Desktop applies automatically; mobile uses explicit Apply button.
    if (!mobileOpen.value) {
      scheduleAutoApply()
    }
  },
  { deep: true }
)

function apply(): void {
  emit('apply', {
    dateRange: localDateRange.value,
    assetType: (localAssetType.value || null) as any,
    department: (localDepartment.value || null) as any,
  })
}

function applyAndClose(): void {
  apply()
  mobileOpen.value = false
}

function clear(): void {
  localDateRange.value = null
  localAssetType.value = ''
  localDepartment.value = ''
  emit('clear')
  mobileOpen.value = false
}
</script>


