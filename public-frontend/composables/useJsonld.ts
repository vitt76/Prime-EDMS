/**
 * JSON-LD (Schema.org) composable for SEO.
 * Use for Organization, SoftwareApplication, BlogPosting, etc.
 */
export function useJsonld() {
  const config = useRuntimeConfig()
  const siteUrl = (config.public.siteUrl as string)?.replace(/\/$/, '') || 'http://localhost:3000'

  const { setJsonLd } = useSeo()

  /** Set one or more JSON-LD scripts (array of schemas). */
  const setSchema = (schema: Record<string, unknown> | Record<string, unknown>[]) => {
    const list = Array.isArray(schema) ? schema : [schema]
    setJsonLd(list.length > 1 ? { '@graph': list } : list[0])
  }

  /** Organization schema (MADDAM / ООО «Мэддам»). */
  const organizationSchema = (overrides: Partial<Record<string, unknown>> = {}) => ({
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'MADDAM',
    alternateName: 'ООО «Мэддам»',
    url: siteUrl,
    logo: `${siteUrl}/logo.png`,
    description: 'Система управления цифровыми активами (DAM). AI-метаданные, аналитика, ФЗ-152.',
    ...overrides
  })

  /** SoftwareApplication schema for the product. */
  const softwareApplicationSchema = (overrides: Partial<Record<string, unknown>> = {}) => ({
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'MADDAM',
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web',
    url: siteUrl,
    ...overrides
  })

  return {
    setSchema,
    setJsonLd,
    siteUrl,
    organizationSchema,
    softwareApplicationSchema
  }
}
