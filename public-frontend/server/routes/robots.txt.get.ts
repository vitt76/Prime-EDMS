/**
 * Dynamic robots.txt for SEO (Yandex Host, Sitemap URL).
 * Uses NUXT_PUBLIC_SITE_URL (e.g. https://maddam.io in production).
 */
export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl || 'http://localhost:3000'
  const base = siteUrl.replace(/\/$/, '')
  const host = new URL(base).host

  const body = [
    '# https://www.robotstxt.org/robotstxt.html',
    'User-agent: *',
    'Allow: /',
    'Allow: /pricing',
    'Allow: /about',
    'Allow: /blog',
    'Allow: /contact',
    'Allow: /roadmap',
    'Allow: /changelog',
    'Allow: /privacy',
    'Allow: /terms',
    '',
    'Disallow: /auth/',
    'Disallow: /admin',
    'Disallow: /app/',
    'Disallow: /account/',
    'Disallow: /api/',
    'Disallow: /_nuxt/',
    'Disallow: /__nuxt_error',
    '',
    'User-agent: Googlebot',
    'Allow: /',
    '',
    'User-agent: Yandex',
    'Allow: /',
    '',
    `Host: ${host}`,
    '',
    `Sitemap: ${base}/sitemap.xml`
  ].join('\n')

  setHeader(event, 'Content-Type', 'text/plain; charset=utf-8')
  setHeader(event, 'Cache-Control', 'public, max-age=3600')
  return body
})
