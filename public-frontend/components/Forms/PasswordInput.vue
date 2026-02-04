<template>
  <div>
    <FormsFormInput
      v-bind="$attrs"
      :model-value="modelValue"
      @update:model-value="onInput"
      type="password"
    />

    <div v-if="showStrengthMeter && modelValue" class="mt-2">
      <div class="flex gap-1">
        <div
          v-for="i in 4"
          :key="i"
          class="h-1 flex-1 rounded-full transition"
          :class="i <= strength ? strengthColor : 'bg-neutral-200'"
        ></div>
      </div>
      <p class="mt-1 text-xs" :class="strengthTextClass">
        {{ strengthText }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: string
  showStrengthMeter?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const strength = computed(() => {
  let score = 0
  if (props.modelValue.length >= 8) score += 1
  if (/[a-z]/.test(props.modelValue) && /[A-Z]/.test(props.modelValue)) score += 1
  if (/[0-9]/.test(props.modelValue)) score += 1
  if (/[!@#$%^&*]/.test(props.modelValue)) score += 1
  return score
})

const strengthColor = computed(() => {
  const colors = ['bg-error', 'bg-warning', 'bg-info', 'bg-success']
  return colors[Math.max(0, strength.value - 1)]
})

const strengthText = computed(() => {
  const texts = ['Слабый', 'Средний', 'Хороший', 'Отличный']
  return texts[Math.max(0, strength.value - 1)]
})

const strengthTextClass = computed(() => {
  const classes = ['text-error', 'text-warning', 'text-info', 'text-success']
  return classes[Math.max(0, strength.value - 1)]
})

const onInput = (value: string) => {
  emit('update:modelValue', value)
}
</script>
