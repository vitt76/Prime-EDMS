<template>
  <div>
    <SEOPageMeta
      :title="page?.meta_title || 'DAM-система для управления медиафайлами | MADDAM'"
      :description="page?.meta_description"
      :og-image="page?.og_image"
      :canonical="page?.canonical_url"
    />
    <SEOJsonLd :schema="jsonLd" />

    <SectionsHeroSection
      v-animate-on-scroll="'fade-up'"
      :heading="hero.heading"
      :subheading="hero.subheading"
      :cta-text="hero.cta_text"
      :cta-url="hero.cta_url"
      :demo-text="$t('cta.demo')"
      :badge="hero.badge"
    />
    
    <SectionsFeaturesSection v-animate-on-scroll:100="'fade-up'" />
    
    <SectionsSocialProofSection v-animate-on-scroll:200="'slide-up'" />
    
    <SectionsPricingSection v-animate-on-scroll:100="'fade-up'" :plans="plans" />
    
    <SectionsCTASection v-animate-on-scroll="'scale'" />
  </div>
</template>

<script setup lang="ts">
import type { PublicPage, PublicPlan } from '~/types/content'

const { getPage, getPlans } = useApi()
const { locale } = useI18n()

const { data: page } = await useAsyncData<PublicPage | null>(
  `home-page-${locale.value}`,
  () => getPage('home', locale.value).catch(() => null),
  { watch: [locale] }
)

const { data: plans } = await useAsyncData<PublicPlan[]>(
  `plans-${locale.value}`,
  () => getPlans(locale.value),
  { default: () => [], watch: [locale] }
)

const hero = computed(() => {
  const heroSection = page.value?.sections?.find((s) => s.type === 'hero')
  return {
    heading: heroSection?.content?.heading || 'Управляйте контентом быстрее, чем когда-либо',
    subheading: heroSection?.content?.subheading || 'Облачное хранилище + AI-поиск + Аналитика для вашей команды',
    cta_text: heroSection?.content?.cta_text || 'Начать бесплатно',
    cta_url: heroSection?.content?.cta_url || '/auth/register',
    badge: heroSection?.content?.badge || 'Новинка: AI Search 2.0'
  }
})

const jsonLd = computed(() => ({
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'MADDAM',
  description: page.value?.meta_description || 'Облачная DAM-система для управления медиафайлами',
  url: page.value?.canonical_url || 'http://localhost:3000',
  applicationCategory: 'BusinessApplication',
  offers: {
    '@type': 'AggregateOffer',
    priceCurrency: 'USD',
    lowPrice: '29',
    highPrice: 'custom',
    offerCount: '3'
  },
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.8',
    ratingCount: '250'
  }
}))
</script>
