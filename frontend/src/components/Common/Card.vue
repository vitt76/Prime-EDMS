<template>
  <div :class="cardClasses">
    <div v-if="$slots.header" class="px-4 py-3 border-b border-neutral-300 dark:border-neutral-300">
      <slot name="header" />
    </div>
    <div :class="bodyClasses">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-4 py-3 border-t border-neutral-300 dark:border-neutral-300">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'elevated' | 'outlined'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  padding: 'md',
  hover: false
})

const cardClasses = computed(() => {
  const base = 'bg-neutral-0 dark:bg-neutral-0 rounded-lg border border-neutral-300 dark:border-neutral-300 transition-all duration-fast'
  
  const variants = {
    default: 'shadow-sm',
    elevated: 'shadow-md',
    outlined: 'shadow-none'
  }
  
  const hoverClass = props.hover ? 'hover:shadow-lg cursor-pointer' : ''
  
  return `${base} ${variants[props.variant]} ${hoverClass}`
})

const bodyClasses = computed(() => {
  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6'
  }
  
  return paddings[props.padding]
})
</script>


