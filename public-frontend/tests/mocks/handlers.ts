/**
 * MSW Request Handlers
 * 
 * Mock API responses for testing
 */
import { http, HttpResponse } from 'msw'

// Mock data
const mockPage = {
  id: '1',
  slug: 'home',
  title: 'Главная',
  meta_title: 'MADDAM - DAM система для управления медиафайлами',
  meta_description: 'Облачная DAM-система для управления медиафайлами',
  sections: [
    {
      id: '1',
      type: 'hero',
      order: 1,
      content: {
        heading: 'Управляйте контентом быстрее',
        subheading: 'Облачное хранилище + AI-поиск',
        cta_text: 'Начать бесплатно',
        cta_url: '/auth/register'
      }
    }
  ]
}

const mockPlans = [
  {
    id: '1',
    name: 'Starter',
    description: 'Для небольших команд',
    price_monthly: 29,
    price_yearly: 278,
    currency: 'USD',
    features: ['5 пользователей', '10 ГБ хранилища'],
    recommended: false,
    type: 'saas'
  },
  {
    id: '2',
    name: 'Professional',
    description: 'Для растущих компаний',
    price_monthly: 99,
    price_yearly: 950,
    currency: 'USD',
    features: ['25 пользователей', '100 ГБ хранилища'],
    recommended: true,
    type: 'saas'
  },
  {
    id: '3',
    name: 'Enterprise',
    description: 'Для крупных организаций',
    price_monthly: null,
    price_yearly: null,
    currency: 'USD',
    features: ['Неограниченно пользователей', 'Неограниченно хранилища'],
    recommended: false,
    type: 'standalone'
  }
]

const mockPosts = [
  {
    id: '1',
    slug: 'introducing-ai-search',
    title: 'Introducing AI Search 2.0',
    excerpt: 'Our new AI-powered search makes finding files faster than ever.',
    content: '<p>Full article content here...</p>',
    featured_image: 'https://placeholder.co/800x400',
    author_name: 'Anna Petrova',
    author_avatar: 'https://placeholder.co/100x100',
    category: 'Product',
    tags: ['AI', 'Search', 'Update'],
    published_at: '2025-01-15T10:00:00Z',
    reading_time_minutes: 5
  },
  {
    id: '2',
    slug: 'best-practices-dam',
    title: 'Best Practices for Digital Asset Management',
    excerpt: 'Learn how to organize your digital assets effectively.',
    content: '<p>Full article content here...</p>',
    featured_image: 'https://placeholder.co/800x400',
    author_name: 'Mikhail Sidorov',
    author_avatar: 'https://placeholder.co/100x100',
    category: 'Guide',
    tags: ['DAM', 'Best Practices'],
    published_at: '2025-01-10T10:00:00Z',
    reading_time_minutes: 8
  }
]

const mockFaqs = [
  {
    id: '1',
    section: 'general',
    question: 'What is MADDAM?',
    answer: 'MADDAM is a cloud-based DAM system for managing digital assets.',
    order: 1
  },
  {
    id: '2',
    section: 'pricing',
    question: 'Can I upgrade my plan later?',
    answer: 'Yes, you can upgrade or downgrade your plan at any time.',
    order: 1
  }
]

export const handlers = [
  // Pages
  http.get('/api/v4/public/pages/:slug/', ({ params }) => {
    if (params.slug === 'home') {
      return HttpResponse.json(mockPage)
    }
    return new HttpResponse(null, { status: 404 })
  }),

  // Plans
  http.get('/api/v4/public/plans/', () => {
    return HttpResponse.json(mockPlans)
  }),

  // Posts list
  http.get('/api/v4/public/posts/', ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const limit = parseInt(url.searchParams.get('limit') || '10')
    const search = url.searchParams.get('search') || ''

    let filteredPosts = mockPosts
    if (search) {
      filteredPosts = mockPosts.filter(
        p => p.title.toLowerCase().includes(search.toLowerCase())
      )
    }

    return HttpResponse.json({
      count: filteredPosts.length,
      next: null,
      previous: null,
      results: filteredPosts.slice((page - 1) * limit, page * limit)
    })
  }),

  // Post detail
  http.get('/api/v4/public/posts/:slug/', ({ params }) => {
    const post = mockPosts.find(p => p.slug === params.slug)
    if (post) {
      return HttpResponse.json(post)
    }
    return new HttpResponse(null, { status: 404 })
  }),

  // FAQs
  http.get('/api/v4/public/faq/', ({ request }) => {
    const url = new URL(request.url)
    const section = url.searchParams.get('section')

    let faqs = mockFaqs
    if (section) {
      faqs = mockFaqs.filter(f => f.section === section)
    }

    return HttpResponse.json(faqs)
  }),

  // Lead creation
  http.post('/api/v4/public/leads/', async ({ request }) => {
    const body = await request.json() as any
    return HttpResponse.json({
      id: '1',
      message: 'Lead created successfully',
      ...body
    }, { status: 201 })
  }),

  // Registration
  http.post('/api/v4/public/auth/register/', async ({ request }) => {
    const body = await request.json() as any
    
    if (body.email === 'existing@example.com') {
      return HttpResponse.json(
        { email: ['This email is already registered'] },
        { status: 400 }
      )
    }

    return HttpResponse.json({
      email: body.email,
      message: 'Registration successful. Please check your email.'
    }, { status: 201 })
  }),

  // Login
  http.post('/api/v4/public/auth/login/', async ({ request }) => {
    const body = await request.json() as any

    if (body.email === 'inactive@example.com') {
      return HttpResponse.json(
        { message: 'Аккаунт не активирован. Подтвердите email перед входом.', error: 'account_inactive' },
        { status: 403 }
      )
    }

    if (body.email !== 'demo@example.com' || body.password !== 'Password123!') {
      return HttpResponse.json(
        { message: 'Неверный email или пароль.' },
        { status: 401 }
      )
    }

    return HttpResponse.json({
      token: 'demo-token',
      user: {
        id: '1',
        email: body.email,
        username: body.email
      },
      redirect_url: 'http://localhost:5173'
    })
  }),

  // Email verification
  http.post('/api/v4/public/auth/verify-email/', async ({ request }) => {
    const body = await request.json() as any
    if (body.token === 'invalid-token') {
      return HttpResponse.json(
        { message: 'Invalid or expired token' },
        { status: 400 }
      )
    }
    return HttpResponse.json({
      message: 'Email verified successfully',
      redirect_url: '/auth/login'
    })
  }),

  // Public analytics events
  http.post('/api/v4/public/analytics/events/', () => {
    return HttpResponse.json({ status: 'accepted' }, { status: 202 })
  }),

  // Newsletter subscription
  http.post('/api/v4/public/newsletter/', async ({ request }) => {
    const body = await request.json() as any
    return HttpResponse.json({
      message: 'Subscribed successfully',
      email: body.email
    }, { status: 201 })
  })
]
