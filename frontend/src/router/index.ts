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
  // Collection Pages (Sidebar navigation)
  {
    path: '/dam/favorites',
    name: 'dam-favorites',
    component: () => import('@/pages/collections/FavoritesPage.vue'),
    meta: { requiresAuth: true, title: 'Избранное' }
  },
  {
    path: '/dam/my-uploads',
    name: 'dam-my-uploads',
    component: () => import('@/pages/collections/MyUploadsPage.vue'),
    meta: { requiresAuth: true, title: 'Мои загрузки' }
  },
  {
    path: '/dam/recent',
    name: 'dam-recent',
    component: () => import('@/pages/collections/RecentPage.vue'),
    meta: { requiresAuth: true, title: 'Недавние' }
  },
  {
    path: '/dam/shared',
    name: 'dam-shared',
    component: () => import('@/pages/collections/SharedWithMePage.vue'),
    meta: { requiresAuth: true, title: 'Доступные мне' }
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
  {
    path: '/sharing/:id',
    name: 'sharing-detail',
    component: () => import('@/pages/SharingDetailPage.vue'),
    meta: { requiresAuth: true, title: 'Детали ссылки' },
    props: true
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
  // Admin routes (new Admin Panel with AdminLayout)
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      breadcrumb: 'Administration'
    },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: () => import('@/pages/admin/AdminDashboard.vue'),
        meta: { title: 'Обзор - Admin' }
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/pages/admin/AdminUsers.vue'),
        meta: { title: 'Пользователи - Admin' }
      },
      {
        path: 'users/:id',
        name: 'admin-user-detail',
        component: () => import('@/pages/admin/AdminUserDetail.vue'),
        meta: { title: 'Пользователь - Admin' }
      },
      {
        path: 'roles',
        name: 'admin-roles',
        component: () => import('@/pages/admin/AdminRoles.vue'),
        meta: { title: 'Роли - Admin' }
      },
      {
        path: 'metadata',
        name: 'admin-metadata',
        component: () => import('@/pages/admin/AdminMetadata.vue'),
        meta: { title: 'Метаданные - Admin' }
      },
      {
        path: 'workflows',
        name: 'admin-workflows',
        component: () => import('@/pages/admin/AdminWorkflows.vue'),
        meta: { title: 'Рабочие процессы - Admin' }
      },
      {
        path: 'workflows/:id',
        name: 'admin-workflow-detail',
        component: () => import('@/pages/admin/AdminWorkflowDetail.vue'),
        meta: { title: 'Рабочий процесс - Admin' }
      },
      {
        path: 'sources',
        name: 'admin-sources',
        component: () => import('@/pages/admin/AdminSources.vue'),
        meta: { title: 'Источники - Admin' }
      },
      {
        path: 'ai-logs',
        name: 'admin-ai-logs',
        component: () => import('@/pages/admin/AdminAILogs.vue'),
        meta: { title: 'AI-обработка - Admin' }
      },
      {
        path: 'health',
        name: 'admin-health',
        component: () => import('@/pages/admin/AdminHealth.vue'),
        meta: { title: 'Мониторинг - Admin' }
      },
      {
        path: 'logs',
        name: 'admin-logs',
        component: () => import('@/pages/admin/AdminLogs.vue'),
        meta: { title: 'Логи - Admin' }
      },
      {
        path: 'storage',
        name: 'admin-storage',
        component: () => import('@/pages/admin/AdminStorage.vue'),
        meta: { title: 'Хранилище S3 - Admin' }
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
    const authResult = await authStore.checkAuth()
    // If auth check failed and we're not on login page, redirect
    if (!authResult && to.name !== 'login' && to.meta.requiresAuth) {
      next({
        name: 'login',
        query: { returnTo: to.fullPath }
      })
      return
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

  // Check admin access
  if (to.meta.requiresAdmin) {
    const u = authStore.user as any
    const perms: string[] = (authStore.permissions as any) || u?.permissions || []
    const hasAdminPerm =
      Array.isArray(perms) &&
      perms.some((p) =>
        String(p).startsWith('user_management.user_') ||
        String(p).startsWith('user_management.group_') ||
        String(p).startsWith('permissions.role_')
      )
    const isAdmin = !!u && (u.is_staff === true || u.is_superuser === true || u.can_access_admin_panel === true || hasAdminPerm)

    if (!isAdmin) {
      console.warn(
        `Access denied: User ${authStore.user?.id} attempted ${to.path}, requires admin`
      )
      next({
        name: 'forbidden',
        query: {
          returnTo: to.fullPath,
          requiredRole: 'admin'
        }
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


