<template>
  <div class="relative" ref="selectRef">
    <!-- Select Button -->
    <button
      :type="type"
      :disabled="disabled"
      :class="selectClasses"
      @click="toggleDropdown"
      @keydown.enter.prevent="toggleDropdown"
      @keydown.space.prevent="toggleDropdown"
      @keydown.escape="closeDropdown"
      :aria-expanded="isOpen"
      :aria-haspopup="true"
      :aria-label="label || placeholder"
    >
      <span v-if="selectedLabel" class="text-neutral-900 dark:text-neutral-900">
        {{ selectedLabel }}
      </span>
      <span v-else class="text-neutral-500 dark:text-neutral-500">
        {{ placeholder }}
      </span>
      <svg
        :class="[
          'w-5 h-5 transition-transform',
          isOpen ? 'transform rotate-180' : ''
        ]"
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
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-1 w-full bg-neutral-0 dark:bg-neutral-0 border border-neutral-300 dark:border-neutral-300 rounded-md shadow-lg max-h-60 overflow-auto"
        @click.stop
      >
        <!-- Search Input (if searchable) -->
        <div v-if="searchable" class="p-2 border-b border-neutral-300 dark:border-neutral-300">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск..."
            class="w-full px-3 py-2 text-sm border border-neutral-300 dark:border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            @click.stop
            @keydown.escape.stop="closeDropdown"
          />
        </div>

        <!-- Options List -->
        <ul class="py-1" role="listbox">
          <li
            v-for="option in filteredOptions"
            :key="getOptionValue(option)"
            :class="[
              'px-3 py-2 text-sm cursor-pointer transition-colors',
              isSelected(option)
                ? 'bg-primary-50 dark:bg-primary-50 text-primary-600 dark:text-primary-600'
                : 'text-neutral-700 dark:text-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-100'
            ]"
            role="option"
            :aria-selected="isSelected(option)"
            @click="selectOption(option)"
            @keydown.enter.prevent="selectOption(option)"
            @keydown.space.prevent="selectOption(option)"
          >
            <div class="flex items-center gap-2">
              <input
                v-if="multiple"
                type="checkbox"
                :checked="isSelected(option)"
                class="w-4 h-4 text-primary-500 rounded border-neutral-300 focus:ring-primary-500"
                @click.stop
              />
              <span>{{ getOptionLabel(option) }}</span>
            </div>
          </li>
        </ul>

        <!-- Empty State -->
        <div
          v-if="filteredOptions.length === 0"
          class="px-3 py-2 text-sm text-neutral-500 dark:text-neutral-500 text-center"
        >
          Нет вариантов
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface Option {
  value: string | number
  label: string
  disabled?: boolean
}

interface Props {
  modelValue?: string | number | (string | number)[]
  options: Option[] | string[]
  placeholder?: string
  label?: string
  disabled?: boolean
  multiple?: boolean
  searchable?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Выберите...',
  disabled: false,
  multiple: false,
  searchable: false,
  type: 'button'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | (string | number)[]]
  change: [value: string | number | (string | number)[]]
}>()

const selectRef = ref<HTMLElement | null>(null)
const isOpen = ref(false)
const searchQuery = ref('')

const selectClasses = computed(() => {
  return [
    'w-full',
    'px-3',
    'py-2',
    'text-sm',
    'text-left',
    'bg-neutral-0',
    'dark:bg-neutral-0',
    'border',
    'border-neutral-300',
    'dark:border-neutral-300',
    'rounded-md',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-primary-500',
    'focus:border-transparent',
    'flex',
    'items-center',
    'justify-between',
    'gap-2',
    props.disabled
      ? 'opacity-50 cursor-not-allowed'
      : 'cursor-pointer hover:border-neutral-400 dark:hover:border-neutral-400'
  ].filter(Boolean).join(' ')
})

const normalizedOptions = computed(() => {
  return props.options.map((opt) => {
    if (typeof opt === 'string') {
      return { value: opt, label: opt }
    }
    return opt
  })
})

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return normalizedOptions.value
  }
  const query = searchQuery.value.toLowerCase()
  return normalizedOptions.value.filter((opt) =>
    opt.label.toLowerCase().includes(query)
  )
})

const selectedLabel = computed(() => {
  if (props.multiple) {
    const selected = (props.modelValue as (string | number)[]) || []
    if (selected.length === 0) return ''
    if (selected.length === 1) {
      const opt = normalizedOptions.value.find(
        (o) => o.value === selected[0]
      )
      return opt?.label || ''
    }
    return `Выбрано: ${selected.length}`
  } else {
    const value = props.modelValue
    if (!value) return ''
    const opt = normalizedOptions.value.find((o) => o.value === value)
    return opt?.label || ''
  }
})

function getOptionValue(option: Option): string | number {
  return option.value
}

function getOptionLabel(option: Option): string {
  return option.label
}

function isSelected(option: Option): boolean {
  if (props.multiple) {
    const selected = (props.modelValue as (string | number)[]) || []
    return selected.includes(option.value)
  } else {
    return props.modelValue === option.value
  }
}

function selectOption(option: Option) {
  if (option.disabled) return

  if (props.multiple) {
    const current = (props.modelValue as (string | number)[]) || []
    const index = current.indexOf(option.value)
    let newValue: (string | number)[]
    if (index === -1) {
      newValue = [...current, option.value]
    } else {
      newValue = current.filter((v) => v !== option.value)
    }
    emit('update:modelValue', newValue)
    emit('change', newValue)
  } else {
    emit('update:modelValue', option.value)
    emit('change', option.value)
    closeDropdown()
  }
}

function toggleDropdown() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchQuery.value = ''
  }
}

function closeDropdown() {
  isOpen.value = false
  searchQuery.value = ''
}

function handleClickOutside(event: MouseEvent) {
  if (selectRef.value && !selectRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

