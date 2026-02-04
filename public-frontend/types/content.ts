export interface PageSection {
  id: string
  type: string
  order: number
  content: Record<string, any>
}

export interface PublicPage {
  id: string
  slug: string
  title: string
  meta_title: string
  meta_description: string
  og_image?: string
  canonical_url?: string
  sections: PageSection[]
}

export interface PublicPost {
  id: string
  slug: string
  title: string
  excerpt?: string
  content?: string
  content_html?: string
  featured_image?: string
  author_name?: string
  author_avatar?: string
  author_role?: string
  category?: string
  tags?: string[]
  published_at?: string
  updated_at?: string
  reading_time_minutes?: number
  seo_title?: string
  seo_description?: string
  og_image?: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface PublicPlan {
  id: string
  name: string
  description?: string
  price_monthly?: number | null
  price_yearly?: number | null
  currency?: string
  billing_period?: string
  features?: string[]
  recommended?: boolean
  type?: string
  cta_text?: string
  cta_url?: string
}

export interface PublicFAQ {
  id: string
  section: string
  question: string
  answer: string
  order: number
}
