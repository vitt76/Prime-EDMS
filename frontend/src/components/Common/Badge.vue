<template>
  <span :class="badgeClasses">
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BadgeVariant } from '@/types'

interface Props {
  variant?: BadgeVariant
  size?: 'sm' | 'md' | 'lg'
  rounded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'neutral',
  size: 'md',
  rounded: true
})

const badgeClasses = computed(() => {
  const base = 'inline-flex items-center font-medium'
  
  const variants = {
    success: 'bg-success/10 text-success border border-success/20',
    warning: 'bg-warning/10 text-warning border border-warning/20',
    error: 'bg-error/10 text-error border border-error/20',
    info: 'bg-info/10 text-info border border-info/20',
    neutral: 'bg-neutral-100 text-neutral-900 border border-neutral-300 dark:bg-neutral-100 dark:text-neutral-900 dark:border-neutral-300'
  }
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  }
  
  const roundedClass = props.rounded ? 'rounded-full' : 'rounded-base'
  
  return `${base} ${variants[props.variant]} ${sizes[props.size]} ${roundedClass}`
})
</script>


