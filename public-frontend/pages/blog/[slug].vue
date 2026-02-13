<template>
  <div class="py-12 lg:py-16">
    <SEOPageMeta
      :title="`${post?.title || 'Статья'} | MADDAM Блог`"
      :description="post?.seo_description || post?.excerpt"
      :og-image="post?.og_image || post?.featured_image"
    />
    <SEOJsonLd :schema="jsonLd" />

    <!-- Breadcrumb -->
    <div class="mx-auto max-w-container px-4">
      <nav class="mb-8 flex items-center gap-2 text-sm text-neutral-500">
        <NuxtLink to="/" class="hover:text-neutral-700">Главная</NuxtLink>
        <ChevronRightIcon class="h-4 w-4" />
        <NuxtLink to="/blog" class="hover:text-neutral-700">Блог</NuxtLink>
        <ChevronRightIcon class="h-4 w-4" />
        <span class="text-neutral-900 line-clamp-1">{{ post?.title }}</span>
      </nav>
    </div>

    <!-- Loading State -->
    <div v-if="pending" class="flex items-center justify-center py-16">
      <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error || !post" class="mx-auto max-w-container px-4 py-16 text-center">
      <ExclamationTriangleIcon class="mx-auto h-12 w-12 text-neutral-300" />
      <h1 class="mt-4 text-2xl font-bold text-neutral-900">Статья не найдена</h1>
      <p class="mt-2 text-neutral-600">
        К сожалению, запрашиваемая статья не существует или была удалена.
      </p>
      <NuxtLink 
        to="/blog" 
        class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        <ArrowLeftIcon class="h-4 w-4" />
        Вернуться к блогу
      </NuxtLink>
    </div>

    <!-- Post Content -->
    <div v-else class="mx-auto max-w-container px-4">
      <BlogPostDetail :post="post" :related-posts="relatedPosts || []" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PublicPost, PaginatedResponse } from '~/types/content'
import { ChevronRightIcon, ArrowLeftIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const { getPost, getPosts } = useApi()
const { locale } = useI18n()
const route = useRoute()

const { data: post, pending, error } = await useAsyncData<PublicPost | null>(
  `blog-detail-${route.params.slug}-${locale.value}`,
  () => getPost(String(route.params.slug), locale.value).catch(() => null),
  { watch: [locale] }
)

// Fetch related posts
const { data: relatedData } = await useAsyncData<PaginatedResponse<PublicPost> | null>(
  `blog-related-${route.params.slug}-${locale.value}`,
  () => {
    if (!post.value?.category) return Promise.resolve(null)
    return getPosts({ 
      lang: locale.value,
      category: post.value.category,
      limit: 3
    }).catch(() => null)
  },
  { watch: [locale, post] }
)

const relatedPosts = computed(() => {
  if (!relatedData.value?.results) return []
  // Filter out the current post
  return relatedData.value.results.filter(p => p.slug !== route.params.slug)
})

const { siteUrl } = useJsonld()
const jsonLd = computed(() => ({
  '@context': 'https://schema.org',
  '@type': 'BlogPosting',
  headline: post.value?.title || '',
  description: post.value?.excerpt || '',
  image: post.value?.featured_image || '',
  datePublished: post.value?.published_at || '',
  dateModified: post.value?.updated_at || post.value?.published_at || '',
  author: {
    '@type': 'Person',
    name: post.value?.author_name || 'MADDAM Team'
  },
  publisher: {
    '@type': 'Organization',
    name: 'MADDAM',
    logo: {
      '@type': 'ImageObject',
      url: `${siteUrl}/logo.png`
    }
  },
  mainEntityOfPage: {
    '@type': 'WebPage',
    '@id': `${siteUrl}/blog/${route.params.slug}`
  }
}))
</script>
