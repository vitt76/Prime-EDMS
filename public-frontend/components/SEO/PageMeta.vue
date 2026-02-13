<template>
  <span />
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    title: string
    description?: string
    ogImage?: string
    canonical?: string
    /** When true, canonical = siteUrl + current route path (if canonical not set) */
    canonicalFromRoute?: boolean
  }>(),
  { canonicalFromRoute: true }
)

const { setPageMeta } = useSeo()
setPageMeta({
  title: props.title,
  description: props.description,
  ogImage: props.ogImage,
  canonical: props.canonical,
  canonicalFromRoute: props.canonicalFromRoute
})
</script>
