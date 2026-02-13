/**
 * SEO composable: page meta (title, description, OG, Twitter), canonical, JSON-LD.
 * Use SEOPageMeta in pages or call setPageMeta/setJsonLd directly.
 */
export function useSeo() {
  const config = useRuntimeConfig()
  const siteUrl = (config.public.siteUrl as string)?.replace(/\/$/, '') || ''

  const setPageMeta = (meta: {
    title: string
    description?: string
    ogImage?: string
    ogType?: string
    canonical?: string
    /** If true and canonical not set, use siteUrl + current path (useRoute().path) */
    canonicalFromRoute?: boolean
  }) => {
    const route = useRoute()
    const canonical = meta.canonical ?? (meta.canonicalFromRoute && siteUrl ? `${siteUrl}${route.path}` : undefined)
    const ogImage = meta.ogImage?.startsWith('http') ? meta.ogImage : meta.ogImage && siteUrl ? `${siteUrl}${meta.ogImage}` : undefined

    useSeoMeta({
      title: meta.title,
      description: meta.description,
      ogTitle: meta.title,
      ogDescription: meta.description,
      ogImage: ogImage || (siteUrl ? `${siteUrl}/og-default.png` : '/og-default.png'),
      ogType: meta.ogType || 'website',
      ogUrl: canonical,
      twitterCard: 'summary_large_image',
      twitterTitle: meta.title,
      twitterDescription: meta.description,
      twitterImage: ogImage
    })

    if (canonical) {
      useHead({
        link: [{ rel: 'canonical', href: canonical }]
      })
    }
  }

  const setJsonLd = (schema: Record<string, any>) => {
    useHead({
      script: [
        {
          type: 'application/ld+json',
          children: JSON.stringify(schema)
        }
      ]
    })
  }

  return { setPageMeta, setJsonLd }
}
