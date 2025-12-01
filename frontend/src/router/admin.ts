/**
 * Admin Panel Routes
 * All routes are lazy-loaded and guarded by requiresAdmin meta flag
 */

import type { RouteRecordRaw } from 'vue-router'

const AdminLayout = () => import('@/layouts/AdminLayout.vue')

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: () => import('@/pages/admin/AdminDashboard.vue'),
        meta: {
          title: 'Обзор',
        },
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/pages/admin/AdminUsers.vue'),
        meta: {
          title: 'Пользователи',
        },
      },
      {
        path: 'users/:id',
        name: 'admin-user-detail',
        component: () => import('@/pages/admin/AdminUserDetail.vue'),
        meta: {
          title: 'Пользователь',
        },
      },
      {
        path: 'roles',
        name: 'admin-roles',
        component: () => import('@/pages/admin/AdminRoles.vue'),
        meta: {
          title: 'Роли и права',
        },
      },
      {
        path: 'metadata',
        name: 'admin-metadata',
        component: () => import('@/pages/admin/AdminMetadata.vue'),
        meta: {
          title: 'Метаданные',
        },
      },
      {
        path: 'workflows',
        name: 'admin-workflows',
        component: () => import('@/pages/admin/AdminWorkflows.vue'),
        meta: {
          title: 'Рабочие процессы',
        },
      },
      {
        path: 'workflows/:id',
        name: 'admin-workflow-detail',
        component: () => import('@/pages/admin/AdminWorkflowDetail.vue'),
        meta: {
          title: 'Рабочий процесс',
        },
      },
      {
        path: 'sources',
        name: 'admin-sources',
        component: () => import('@/pages/admin/AdminSources.vue'),
        meta: {
          title: 'Источники',
        },
      },
      {
        path: 'ai-logs',
        name: 'admin-ai-logs',
        component: () => import('@/pages/admin/AdminAILogs.vue'),
        meta: {
          title: 'AI-обработка',
        },
      },
      {
        path: 'health',
        name: 'admin-health',
        component: () => import('@/pages/admin/AdminHealth.vue'),
        meta: {
          title: 'Мониторинг',
        },
      },
      {
        path: 'logs',
        name: 'admin-logs',
        component: () => import('@/pages/admin/AdminLogs.vue'),
        meta: {
          title: 'Логи',
        },
      },
    ],
  },
]

export default adminRoutes

