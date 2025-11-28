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
    path: '/auth/2fa',
    name: 'two-factor-auth',
    component: () => import('@/pages/Login2FAPage.vue'),
    meta: { requiresAuth: false, title: 'Two-Factor Authentication' }
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
    component: () => import('@/pages/DAMGalleryPage.vue'),
    meta: { requiresAuth: true, title: 'Галерея активов' }
  },
  {
    path: '/dam/gallery-old',
    name: 'dam-gallery-old',
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
  // Unified Sharing Section
  {
    path: '/sharing',
    name: 'sharing',
    component: () => import('@/pages/SharingPage.vue'),
    meta: { requiresAuth: true, title: 'Распространение' }
  },
  // Legacy redirects (backward compatibility)
  {
    path: '/distribution',
    redirect: '/sharing'
  },
  {
    path: '/shared-links',
    redirect: '/sharing'
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
      requiresRole: 'admin',
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
    // Try to check auth status from Django context/session
    await authStore.checkAuth()
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

  // Check 2FA status for authenticated users
  if (authStore.isAuthenticated && to.name !== 'two-factor-auth') {
    // Check if 2FA is enabled and not verified
    if (authStore.requiresTwoFactor && !authStore.isTwoFactorVerified) {
      // Redirect to 2FA verification
      next({
        name: 'two-factor-auth',
        query: { returnTo: to.fullPath }
      })
      return
    }
  }

  // Check if route requires specific permission
  if (to.meta.requiresPermission) {
    const permission = to.meta.requiresPermission as string
    // hasPermission is a computed that returns a function - call it directly
    if (!authStore.hasPermission(permission)) {
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

  // Check role-based access
  if (to.meta.requiresRole) {
    const requiredRole = to.meta.requiresRole as string
    // hasRole is a computed that returns a function - call it directly
    if (!authStore.hasRole(requiredRole)) {
      console.warn(
        `Access denied: User ${authStore.user?.id} with role ${authStore.user?.role} attempted ${to.path}, required role: ${requiredRole}`
      )
      // Redirect to forbidden page
      next({
        name: 'forbidden',
        query: {
          returnTo: to.fullPath,
          requiredRole: requiredRole
        }
      })
      return
    }
  }

  // Redirect authenticated users away from login page
  if (to.name === 'login' && authStore.isAuthenticated && authStore.isTwoFactorVerified) {
    const returnTo = (to.query.returnTo as string) || '/'
    next(returnTo)
    return
  }

  // Allow access to 2FA page for authenticated users who need it
  if (to.name === 'two-factor-auth' && authStore.isAuthenticated) {
    next()
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


