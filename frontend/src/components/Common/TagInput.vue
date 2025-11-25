<template>
  <div class="tag-input" ref="containerRef">
    <div
      class="flex flex-wrap gap-2 p-2 border border-neutral-300 dark:border-neutral-300 rounded-md bg-neutral-0 dark:bg-neutral-0 min-h-[42px] focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-transparent"
      @click="inputRef?.focus()"
    >
      <!-- Selected Tags -->
      <Badge
        v-for="tag in selectedTags"
        :key="tag"
        variant="info"
        size="sm"
        class="flex items-center gap-1"
      >
        {{ tag }}
        <button
          class="ml-1 hover:text-error transition-colors"
          @click.stop="removeTag(tag)"
          aria-label="Удалить тег"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </Badge>

      <!-- Input Field -->
      <input
        ref="inputRef"
        v-model="inputValue"
        type="text"
        :placeholder="placeholder"
        class="flex-1 min-w-[120px] outline-none bg-transparent text-sm text-neutral-900 dark:text-neutral-900"
        @input="handleInput"
        @keydown.enter.prevent="handleEnter"
        @keydown.backspace="handleBackspace"
        @focus="showSuggestions = true"
        @blur="handleBlur"
      />
    </div>

    <!-- Suggestions Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="showSuggestions && filteredSuggestions.length > 0"
        class="absolute z-50 mt-1 w-full bg-neutral-0 dark:bg-neutral-0 border border-neutral-300 dark:border-neutral-300 rounded-md shadow-lg max-h-60 overflow-y-auto"
      >
        <button
          v-for="(suggestion, index) in filteredSuggestions"
          :key="suggestion"
          :class="[
            'w-full text-left px-4 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-100 transition-colors',
            index === selectedIndex ? 'bg-primary-50 dark:bg-primary-50' : ''
          ]"
          @mousedown.prevent="selectSuggestion(suggestion)"
          @mouseenter="selectedIndex = index"
        >
          {{ suggestion }}
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import Badge from './Badge.vue'
import { onClickOutside } from '@vueuse/core'

interface Props {
  modelValue: string[]
  suggestions?: string[]
  placeholder?: string
  allowCustom?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  suggestions: () => [],
  placeholder: 'Введите тег...',
  allowCustom: true
})

const emit = defineEmits<{
  'update:modelValue': [tags: string[]]
}>()

const containerRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
const inputValue = ref('')
const showSuggestions = ref(false)
const selectedIndex = ref(-1)

const selectedTags = computed(() => props.modelValue || [])

const filteredSuggestions = computed(() => {
  if (!inputValue.value) {
    return props.suggestions.filter((s) => !selectedTags.value.includes(s)).slice(0, 10)
  }

  const query = inputValue.value.toLowerCase()
  return props.suggestions
    .filter((s) => s.toLowerCase().includes(query) && !selectedTags.value.includes(s))
    .slice(0, 10)
})

function handleInput() {
  showSuggestions.value = true
  selectedIndex.value = -1
}

function handleEnter() {
  if (selectedIndex.value >= 0 && selectedIndex.value < filteredSuggestions.value.length) {
    selectSuggestion(filteredSuggestions.value[selectedIndex.value])
  } else if (inputValue.value.trim() && props.allowCustom) {
    addTag(inputValue.value.trim())
  }
}

function handleBackspace(event: KeyboardEvent) {
  if (!inputValue.value && selectedTags.value.length > 0) {
    removeTag(selectedTags.value[selectedTags.value.length - 1])
  }
}

function handleBlur() {
  // Delay to allow click events on suggestions
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

function addTag(tag: string) {
  if (tag && !selectedTags.value.includes(tag)) {
    const newTags = [...selectedTags.value, tag]
    emit('update:modelValue', newTags)
    inputValue.value = ''
    showSuggestions.value = false
  }
}

function removeTag(tag: string) {
  const newTags = selectedTags.value.filter((t) => t !== tag)
  emit('update:modelValue', newTags)
}

function selectSuggestion(suggestion: string) {
  addTag(suggestion)
}

// Click outside to close
onClickOutside(containerRef, () => {
  showSuggestions.value = false
})
</script>

<style scoped>
.tag-input {
  position: relative;
  width: 100%;
}
</style>

