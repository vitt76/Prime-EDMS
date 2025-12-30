<template>
  <Card padding="lg">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
      <div>
        <div class="text-xs text-neutral-600 mb-2">Дата</div>
        <DateRangePicker v-model="localDateRange" />
      </div>

      <div>
        <div class="text-xs text-neutral-600 mb-2">Тип ассета</div>
        <select
          v-model="localAssetType"
          class="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm bg-white text-neutral-900"
        >
          <option :value="''">Все</option>
          <option value="images">Images</option>
          <option value="videos">Videos</option>
          <option value="documents">Documents</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="flex gap-2">
        <button
          class="px-3 py-2 text-sm rounded-md bg-primary-600 text-white hover:bg-primary-700"
          @click="apply"
        >
          Применить
        </button>
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          @click="clear"
        >
          Сбросить
        </button>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

import Card from '@/components/Common/Card.vue'
import DateRangePicker from '@/components/Common/DateRangePicker.vue'

const props = defineProps<{
  dateRange: [string, string] | null
  assetType: 'images' | 'videos' | 'documents' | 'other' | null
}>()

const emit = defineEmits<{
  apply: [payload: { dateRange: [string, string] | null; assetType: 'images' | 'videos' | 'documents' | 'other' | null }]
  clear: []
}>()

const localDateRange = ref<[string, string] | null>(props.dateRange)
const localAssetType = ref<string>(props.assetType || '')

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

function apply(): void {
  emit('apply', {
    dateRange: localDateRange.value,
    assetType: (localAssetType.value || null) as any,
  })
}

function clear(): void {
  localDateRange.value = null
  localAssetType.value = ''
  emit('clear')
}
</script>


