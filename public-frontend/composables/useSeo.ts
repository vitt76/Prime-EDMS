export function useSeo() {
  const setPageMeta = (meta: {
    title: string
    description?: string
    ogImage?: string
    ogType?: string
    canonical?: string
  }) => {
    useSeoMeta({
      title: meta.title,
      description: meta.description,
      ogTitle: meta.title,
      ogDescription: meta.description,
      ogImage: meta.ogImage,
      ogType: meta.ogType || 'website',
      twitterCard: 'summary_large_image',
      twitterTitle: meta.title,
      twitterDescription: meta.description,
      twitterImage: meta.ogImage
    })

    if (meta.canonical) {
      useHead({
        link: [{ rel: 'canonical', href: meta.canonical }]
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
