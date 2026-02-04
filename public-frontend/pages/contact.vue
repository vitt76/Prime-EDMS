<template>
  <div class="mx-auto max-w-container px-4 py-12">
    <SEOPageMeta :title="page?.meta_title || 'Contact | MADDAM'" :description="page?.meta_description" />
    <h1 class="text-3xl font-semibold">{{ page?.title || 'Contact' }}</h1>
    <div class="mt-6 grid gap-10 md:grid-cols-2">
      <div v-html="contentHtml" class="prose max-w-none"></div>
      <ContactForm />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PublicPage } from '~/types/content'

const { getPage } = useApi()
const { locale } = useI18n()

const { data: page } = await useAsyncData<PublicPage | null>(
  () => `page-contact-${locale.value}`,
  () => getPage('contact', locale.value).catch(() => null),
  { watch: [locale] }
)

const contentHtml = computed(() => {
  const section = page.value?.sections?.[0]
  return section?.content?.html || '<p>Свяжитесь с нами через форму.</p>'
})
</script>
