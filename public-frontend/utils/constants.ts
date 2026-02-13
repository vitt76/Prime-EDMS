export const API_ENDPOINTS = {
  PAGES: '/api/v4/public/pages',
  POSTS: '/api/v4/public/posts',
  PLANS: '/api/v4/public/plans',
  FAQ: '/api/v4/public/faq',
  LEADS: '/api/v4/public/leads',
  NEWSLETTER: '/api/v4/public/newsletter',
  LEGAL: {
    CONSENT: '/api/v4/public/legal/consent/'
  },
  AUTH: {
    REGISTER: '/api/v4/public/auth/register',
    LOGIN: '/api/v4/public/auth/login',
    VERIFY: '/api/v4/public/auth/verify-email'
  }
} as const

export const CACHE_TTL = {
  HOMEPAGE: 3600,
  PRICING: 21600,
  BLOG_LIST: 1800,
  BLOG_POST: 3600,
  STATIC_PAGES: 86400
} as const

export const SOCIAL_LINKS = {
  LINKEDIN: 'https://linkedin.com/company/maddam',
  TWITTER: 'https://twitter.com/maddam_dam',
  GITHUB: 'https://github.com/maddam'
} as const

export const READING_SPEED_WPM = 200
