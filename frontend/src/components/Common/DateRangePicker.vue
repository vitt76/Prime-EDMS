<template>
  <div class="date-range-picker" ref="containerRef">
    <div class="flex gap-2">
      <div class="flex-1">
        <label class="block text-xs text-neutral-600 dark:text-neutral-600 mb-1">
          От
        </label>
        <input
          v-model="startDate"
          type="date"
          class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          @change="handleDateChange"
        />
      </div>
      <div class="flex-1">
        <label class="block text-xs text-neutral-600 dark:text-neutral-600 mb-1">
          До
        </label>
        <input
          v-model="endDate"
          type="date"
          :min="startDate"
          class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          @change="handleDateChange"
        />
      </div>
    </div>

    <!-- Quick Presets -->
    <div class="mt-2 flex flex-wrap gap-2">
      <button
        v-for="preset in presets"
        :key="preset.value"
        :class="[
          'px-2 py-1 text-xs rounded-md transition-colors',
          isPresetActive(preset.value)
            ? 'bg-primary-500 text-white'
            : 'bg-neutral-100 dark:bg-neutral-100 text-neutral-700 dark:text-neutral-700 hover:bg-neutral-200 dark:hover:bg-neutral-200'
        ]"
        @click="applyPreset(preset.value)"
      >
        {{ preset.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  modelValue?: [string, string] | null
}

const emit = defineEmits<{
  'update:modelValue': [value: [string, string] | null]
}>()

const props = defineProps<Props>()

const containerRef = ref<HTMLElement | null>(null)
const startDate = ref('')
const endDate = ref('')

const presets = [
  { value: 'today', label: 'Сегодня', getDates: () => getTodayRange() },
  { value: 'week', label: 'Неделя', getDates: () => getWeekRange() },
  { value: 'month', label: 'Месяц', getDates: () => getMonthRange() },
  { value: 'year', label: 'Год', getDates: () => getYearRange() }
]

const activePreset = ref<string | null>(null)

// Initialize from modelValue
watch(
  () => props.modelValue,
  (value) => {
    if (value && value.length === 2) {
      startDate.value = value[0]
      endDate.value = value[1]
      activePreset.value = null
    } else {
      startDate.value = ''
      endDate.value = ''
      activePreset.value = null
    }
  },
  { immediate: true }
)

function handleDateChange() {
  if (startDate.value && endDate.value) {
    emit('update:modelValue', [startDate.value, endDate.value])
    activePreset.value = null
  } else {
    emit('update:modelValue', null)
  }
}

function isPresetActive(presetValue: string): boolean {
  return activePreset.value === presetValue
}

function applyPreset(presetValue: string) {
  const preset = presets.find((p) => p.value === presetValue)
  if (preset) {
    const [start, end] = preset.getDates()
    startDate.value = start
    endDate.value = end
    activePreset.value = presetValue
    emit('update:modelValue', [start, end])
  }
}

function getTodayRange(): [string, string] {
  const today = new Date().toISOString().split('T')[0]
  return [today, today]
}

function getWeekRange(): [string, string] {
  const today = new Date()
  const weekAgo = new Date(today)
  weekAgo.setDate(today.getDate() - 7)
  return [weekAgo.toISOString().split('T')[0], today.toISOString().split('T')[0]]
}

function getMonthRange(): [string, string] {
  const today = new Date()
  const monthAgo = new Date(today)
  monthAgo.setMonth(today.getMonth() - 1)
  return [monthAgo.toISOString().split('T')[0], today.toISOString().split('T')[0]]
}

function getYearRange(): [string, string] {
  const today = new Date()
  const yearAgo = new Date(today)
  yearAgo.setFullYear(today.getFullYear() - 1)
  return [yearAgo.toISOString().split('T')[0], today.toISOString().split('T')[0]]
}
</script>

<style scoped>
.date-range-picker {
  width: 100%;
}
</style>

