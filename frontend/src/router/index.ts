import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useUiStore } from '@/stores/uiStore'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dam',
    name: 'dam',
    component: () => import('@/pages/DAMPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dam/gallery',
    name: 'dam-gallery',
    component: () => import('@/pages/DAMPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dam/search',
    name: 'dam-search',
    component: () => import('@/pages/AdvancedSearchPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dam/assets/:id',
    name: 'asset-detail',
    component: () => import('@/pages/AssetDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/pages/SettingsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings/profile',
    name: 'settings-profile',
    component: () => import('@/pages/SettingsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/distribution',
    name: 'distribution',
    component: () => import('@/pages/DistributionPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/pages/NotFoundPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const uiStore = useUiStore()

  // Check authentication status
  if (!authStore.isAuthenticated) {
    const token = localStorage.getItem('auth_token')
    if (token) {
      // Try to restore session
      const isAuthenticated = await authStore.checkAuth()
      if (!isAuthenticated) {
        // Token invalid, clear it
        localStorage.removeItem('auth_token')
      }
    }
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login with return URL
    next({
      name: 'login',
      query: { returnTo: to.fullPath }
    })
    return
  }

  // Redirect authenticated users away from login page
  if (to.name === 'login' && authStore.isAuthenticated) {
    const returnTo = (to.query.returnTo as string) || '/'
    next(returnTo)
    return
  }

  // Update breadcrumbs
  const breadcrumbs = generateBreadcrumbs(to)
  uiStore.setBreadcrumbs(breadcrumbs)

  next()
})

function generateBreadcrumbs(to: any) {
  const breadcrumbs: Array<{ label: string; path: string }> = [
    { label: 'Главная', path: '/' }
  ]

  if (to.path !== '/') {
    const pathParts = to.path.split('/').filter(Boolean)
    let currentPath = ''

    pathParts.forEach((part: string, index: number) => {
      currentPath += `/${part}`
      const label = part
        .split('-')
        .map((p: string) => p.charAt(0).toUpperCase() + p.slice(1))
        .join(' ')
      breadcrumbs.push({ label, path: currentPath })
    })
  }

  return breadcrumbs
}

export default router


