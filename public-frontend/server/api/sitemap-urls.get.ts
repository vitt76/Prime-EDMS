/**
 * Dynamic sitemap URLs for blog posts (consumed by @nuxtjs/sitemap via sources).
 * Fetches slugs from Django API; returns array of { loc, lastmod? }.
 */
interface PostItem {
  slug?: string
  updated_at?: string
  published_at?: string
}

interface PaginatedPosts {
  results?: PostItem[]
  count?: number
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const base = (config.public.siteUrl || 'http://localhost:3000').replace(/\/$/, '')
  const apiBase = config.apiBase || 'http://localhost:8080'

  try {
    const data = await $fetch<PaginatedPosts>(`${apiBase}/api/v4/public/posts/`, {
      params: { limit: 500 },
      headers: { Accept: 'application/json' }
    })
    const results = data?.results || []
    const urls = results
      .filter((p): p is PostItem & { slug: string } => Boolean(p?.slug))
      .map((p) => ({
        loc: `/blog/${p.slug}`,
        lastmod: p.updated_at || p.published_at || undefined
      }))
    setHeader(event, 'Cache-Control', 'public, max-age=3600')
    return urls
  } catch {
    setHeader(event, 'Cache-Control', 'public, max-age=60')
    return []
  }
})
