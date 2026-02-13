<template>
  <div class="mx-auto max-w-container px-4 py-12">
    <SEOPageMeta :title="title" :description="metaDescription" />
    <h1 class="text-3xl font-semibold text-neutral-900 dark:text-neutral-100">{{ title }}</h1>
    <div class="prose prose-neutral mt-6 max-w-none dark:prose-invert" v-html="contentHtml"></div>
  </div>
</template>

<script setup lang="ts">
const LEGAL_TITLE = 'Политика конфиденциальности'

const { data } = await useAsyncData('legal-privacy', async () => {
  const raw = await $fetch<string>('/legal/privacy-policy-ru.md', { responseType: 'text' })
  const MarkdownIt = (await import('markdown-it')).default
  const md = new MarkdownIt()
  const html = md.render(raw)
  const titleMatch = raw.match(/^#\s+(.+)$/m)
  const title = titleMatch ? titleMatch[1].trim() : LEGAL_TITLE
  return { html, title }
})

const title = data.value?.title ?? LEGAL_TITLE
const contentHtml = data.value?.html ?? ''
const metaDescription = 'Политика конфиденциальности ООО «Мэддам». Обработка персональных данных в соответствии с 152-ФЗ.'
</script>
