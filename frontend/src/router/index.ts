import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/DashboardPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/pages/DashboardPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/auth/forgot-password',
    name: 'forgot-password',
    component: () => import('@/pages/auth/ForgotPasswordPage.vue'),
    meta: { requiresAuth: false, title: 'Forgot Password' }
  },
  {
    path: '/auth/reset-password',
    name: 'reset-password',
    component: () => import('@/pages/auth/ResetPasswordPage.vue'),
    meta: { requiresAuth: false, title: 'Reset Password' }
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
    path: '/distribution/publications/:id',
    name: 'publication-detail',
    component: () => import('@/pages/PublicationDetailPage.vue'),
    meta: {
      requiresAuth: true,
      breadcrumb: 'Publication Detail',
      title: 'Publication Detail'
    },
    props: true
  },
  // Admin routes (nested structure)
  {
    path: '/admin',
    component: () => import('@/pages/AdminPage.vue'),
    meta: {
      requiresAuth: true,
      requiresPermission: 'admin.access',
      breadcrumb: 'Administration'
    },
    redirect: '/admin/users',
    children: [
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/pages/admin/UserManagementPage.vue'),
        meta: {
          requiresAuth: true,
          requiresPermission: 'admin.user_manage',
          breadcrumb: 'User Management',
          title: 'User Management - Admin'
        }
      },
      {
        path: 'schemas',
        name: 'admin-metadata-schemas',
        component: () => import('@/pages/admin/MetadataSchemaPage.vue'),
        meta: {
          requiresAuth: true,
          requiresPermission: 'admin.schema_manage',
          breadcrumb: 'Metadata Schemas',
          title: 'Metadata Schemas - Admin'
        }
      },
      {
        path: 'workflows',
        name: 'admin-workflows',
        component: () => import('@/pages/admin/WorkflowDesignerPage.vue'),
        meta: {
          requiresAuth: true,
          requiresPermission: 'admin.workflow_manage',
          breadcrumb: 'Workflow Designer',
          title: 'Workflow Designer - Admin'
        }
      },
      {
        path: 'integrations',
        name: 'admin-integrations',
        component: () => import('@/pages/admin/AdminIntegrationsPage.vue'),
        meta: {
          requiresAuth: true,
          requiresPermission: 'admin.integrations_manage',
          breadcrumb: 'Integrations',
          title: 'Integrations - Admin'
        }
      },
      {
        path: 'reports',
        name: 'admin-reports',
        component: () => import('@/pages/admin/AdminReportsPage.vue'),
        meta: {
          requiresAuth: true,
          requiresPermission: 'admin.reports_view',
          breadcrumb: 'Reports',
          title: 'Admin Reports'
        }
      }
    ]
  },
  {
    path: '/collections',
    name: 'collections',
    component: () => import('@/pages/CollectionsPage.vue'),
    meta: {
      requiresAuth: true,
      breadcrumb: 'Collections',
      title: 'Collections'
    }
  },
  {
    path: '/collections/:id',
    name: 'collection-detail',
    component: () => import('@/pages/CollectionsPage.vue'),
    meta: {
      requiresAuth: true,
      breadcrumb: 'Collection Detail',
      title: 'Collection Detail'
    }
  },
  {
    path: '/forbidden',
    name: 'forbidden',
    component: () => import('../pages/ForbiddenPage.vue'),
    meta: { requiresAuth: false }
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
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  const uiStore = useUIStore()

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

  // Check if route requires specific permission
  if (to.meta.requiresPermission) {
    const permission = to.meta.requiresPermission as string
    // hasPermission is a computed that returns a function
    // Type assertion needed because Pinia computed types in router context
    const checkPermission = (authStore.hasPermission as unknown as { value: (p: string) => boolean }).value
    if (!checkPermission(permission)) {
      console.warn(
        `Access denied: User ${authStore.user?.id} attempted ${to.path}, required: ${permission}`
      )
      // Redirect to forbidden page with context
      next({
        name: 'forbidden',
        query: {
          returnTo: to.fullPath,
          requiredPermission: permission
        }
      })
      return
    }
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

    pathParts.forEach((part: string) => {
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


