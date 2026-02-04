<template>
  <span />
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string
  description?: string
  ogImage?: string
  canonical?: string
}>()

const { setPageMeta } = useSeo()
setPageMeta({
  title: props.title,
  description: props.description,
  ogImage: props.ogImage,
  canonical: props.canonical
})
</script>
