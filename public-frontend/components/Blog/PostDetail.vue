<template>
  <article class="mx-auto max-w-3xl">
    <!-- Header -->
    <header class="mb-8">
      <!-- Category -->
      <div v-if="post.category" class="mb-4">
        <span class="inline-flex items-center rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
          {{ post.category }}
        </span>
      </div>

      <!-- Title -->
      <h1 class="text-3xl font-bold leading-tight text-neutral-900 md:text-4xl lg:text-5xl">
        {{ post.title }}
      </h1>

      <!-- Meta -->
      <div class="mt-6 flex flex-wrap items-center gap-4 text-sm text-neutral-500">
        <!-- Author -->
        <div v-if="post.author_name" class="flex items-center gap-2">
          <div 
            v-if="post.author_avatar"
            class="h-10 w-10 overflow-hidden rounded-full"
          >
            <img 
              :src="post.author_avatar"
              :alt="post.author_name"
              class="h-full w-full object-cover"
            />
          </div>
          <div v-else class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-sm font-bold text-white">
            {{ post.author_name.charAt(0).toUpperCase() }}
          </div>
          <div>
            <span class="font-medium text-neutral-900">{{ post.author_name }}</span>
            <p v-if="post.author_role" class="text-xs text-neutral-500">{{ post.author_role }}</p>
          </div>
        </div>

        <span class="text-neutral-300">|</span>

        <!-- Date -->
        <time :datetime="post.published_at" class="flex items-center gap-1">
          <CalendarIcon class="h-4 w-4" />
          {{ formatDate(post.published_at) }}
        </time>

        <span class="text-neutral-300">|</span>

        <!-- Reading Time -->
        <span class="flex items-center gap-1">
          <ClockIcon class="h-4 w-4" />
          {{ post.reading_time_minutes || 5 }} мин чтения
        </span>
      </div>

      <!-- Tags -->
      <div v-if="post.tags?.length" class="mt-4 flex flex-wrap gap-2">
        <span 
          v-for="tag in post.tags" 
          :key="tag" 
          class="inline-flex items-center rounded-full bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-600 transition hover:bg-neutral-200"
        >
          #{{ tag }}
        </span>
      </div>
    </header>

    <!-- Featured Image -->
    <div v-if="post.featured_image" class="mb-10 overflow-hidden rounded-2xl">
      <NuxtImg
        :src="post.featured_image"
        :alt="post.title"
        class="h-auto w-full"
        loading="eager"
        format="webp"
        quality="85"
      />
    </div>

    <!-- Content -->
    <div 
      class="prose prose-lg prose-neutral max-w-none prose-headings:font-semibold prose-a:text-primary-600 prose-a:no-underline hover:prose-a:underline prose-img:rounded-xl"
      v-html="renderedContent"
    />

    <!-- Share & Actions -->
    <div class="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-neutral-200 pt-8">
      <div class="flex items-center gap-4">
        <span class="text-sm font-medium text-neutral-700">Поделиться:</span>
        <div class="flex gap-2">
          <button 
            v-for="social in shareLinks" 
            :key="social.name"
            @click="sharePost(social)"
            class="flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-100 text-neutral-600 transition hover:bg-primary-100 hover:text-primary-600"
            :aria-label="`Share on ${social.name}`"
          >
            <component :is="social.icon" class="h-4 w-4" />
          </button>
        </div>
      </div>

      <NuxtLink 
        to="/blog" 
        class="flex items-center gap-2 text-sm font-medium text-primary-600 transition hover:text-primary-700"
      >
        <ArrowLeftIcon class="h-4 w-4" />
        Все статьи
      </NuxtLink>
    </div>

    <!-- Related Posts -->
    <div v-if="relatedPosts?.length" class="mt-16 border-t border-neutral-200 pt-12">
      <h2 class="text-2xl font-bold text-neutral-900">Похожие статьи</h2>
      <div class="mt-8 grid gap-8 md:grid-cols-2">
        <BlogPostCard v-for="related in relatedPosts.slice(0, 2)" :key="related.id" :post="related" />
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { PublicPost } from '~/types/content'
import { 
  ArrowLeftIcon,
  CalendarIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'
import IconLinkedIn from '~/components/Common/IconLinkedIn.vue'
import IconTwitter from '~/components/Common/IconTwitter.vue'

const props = defineProps<{
  post: PublicPost
  relatedPosts?: PublicPost[]
}>()

const renderedContent = computed(() => {
  // If content is already HTML, return as-is
  // Otherwise, we could use markdown-it to render it
  return props.post.content || ''
})

const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const shareLinks = [
  { name: 'Twitter', icon: IconTwitter, urlTemplate: 'https://twitter.com/intent/tweet?text=' },
  { name: 'LinkedIn', icon: IconLinkedIn, urlTemplate: 'https://www.linkedin.com/sharing/share-offsite/?url=' }
]

const sharePost = (social: typeof shareLinks[0]) => {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(props.post.title)
  let shareUrl = ''
  
  if (social.name === 'Twitter') {
    shareUrl = `${social.urlTemplate}${text}&url=${url}`
  } else {
    shareUrl = `${social.urlTemplate}${url}`
  }
  
  window.open(shareUrl, '_blank', 'width=600,height=400')
}
</script>

<style>
/* Prose styles for rendered content */
.prose img {
  @apply mx-auto;
}

.prose pre {
  @apply rounded-xl bg-neutral-900;
}

.prose code:not(pre code) {
  @apply rounded bg-neutral-100 px-1.5 py-0.5 text-sm;
}
</style>
