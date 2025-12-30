<template>
  <button
    type="button"
    :class="[
      'inline-flex items-center gap-2 px-3 py-2 rounded-full text-sm whitespace-nowrap transition-colors',
      active
        ? 'bg-primary-50 text-primary-700'
        : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
    ]"
  >
    <slot name="icon">
      <span
        v-if="toneDotClass"
        :class="['w-2 h-2 rounded-full', toneDotClass]"
      />
    </slot>
    <span class="font-medium">{{ label }}</span>
    <span :class="[active ? 'text-primary-700' : 'text-neutral-900', 'font-semibold']">{{ count }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  count: number
  active?: boolean
  tone?: 'neutral' | 'success' | 'warning'
}>()

const toneDotClass = computed(() => {
  if (!props.tone || props.tone === 'neutral') return ''
  if (props.tone === 'success') return 'bg-emerald-500'
  if (props.tone === 'warning') return 'bg-amber-500'
  return ''
})
</script>


