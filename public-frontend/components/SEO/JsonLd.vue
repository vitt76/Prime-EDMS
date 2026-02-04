<template>
  <span />
</template>

<script setup lang="ts">
const props = defineProps<{
  schema: Record<string, any>
}>()

const { setJsonLd } = useSeo()
setJsonLd(props.schema)
</script>
