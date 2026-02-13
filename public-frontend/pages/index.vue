<template>
  <div>
    <SEOPageMeta
      :title="page?.meta_title || $t('meta.defaultTitle')"
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

const { t } = useI18n()

const hero = computed(() => {
  const heroSection = page.value?.sections?.find((s) => s.type === 'hero')
  return {
    heading: heroSection?.content?.heading || t('hero.heading'),
    subheading: heroSection?.content?.subheading || t('hero.subheading'),
    cta_text: heroSection?.content?.cta_text || t('cta.start'),
    cta_url: heroSection?.content?.cta_url || '/auth/register',
    badge: heroSection?.content?.badge || t('hero.badge')
  }
})

const { siteUrl, organizationSchema, softwareApplicationSchema } = useJsonld()

const jsonLd = computed(() => {
  const appUrl = page.value?.canonical_url || siteUrl
  const description = page.value?.meta_description || t('meta.defaultDescription')
  return {
    '@context': 'https://schema.org',
    '@graph': [
      organizationSchema({ url: appUrl }),
      {
        ...softwareApplicationSchema({
          description,
          url: appUrl,
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
        })
      }
    ]
  }
})
</script>
