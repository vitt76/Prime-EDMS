<template>
  <div class="mx-auto max-w-container px-4 py-12">
    <SEOPageMeta :title="page?.meta_title || 'Privacy | MADDAM'" :description="page?.meta_description" />
    <h1 class="text-3xl font-semibold">{{ page?.title || 'Privacy' }}</h1>
    <div class="prose mt-6 max-w-none" v-html="contentHtml"></div>
  </div>
</template>

<script setup lang="ts">
import type { PublicPage } from '~/types/content'

const { getPage } = useApi()
const { locale } = useI18n()

const { data: page } = await useAsyncData<PublicPage | null>(
  `page-privacy-${locale.value}`,
  () => getPage('privacy', locale.value).catch(() => null),
  { watch: [locale] }
)

const contentHtml = computed(() => {
  const section = page.value?.sections?.[0]
  return section?.content?.html || '<p>Политика конфиденциальности.</p>'
})
</script>
