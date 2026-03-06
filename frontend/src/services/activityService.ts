import { apiService } from './apiService'

// Интерфейс для ответа HeadlessActivityFeedView
export interface HeadlessActivityFeedResponse {
  count: number
  page: number
  page_size: number
  total_pages: number
  results: HeadlessActivityItem[]
}

export interface HeadlessActivityItem {
  id: number
  timestamp: string
  actor: {
    id: number | null
    username: string
    full_name: string
  } | null  // Может быть null в некоторых случаях
  verb: string  // Переведенный текст
  verb_code: string  // Оригинальный код
  target: {
    id: number
    type: string
    label: string
    url: string | null
  } | null
  description: string
}

// Сохранить существующий интерфейс для обратной совместимости
export interface DashboardActivityItem {
  id: number
  user: string
  user_id: number | null
  action_text: string
  object_name: string | null
  timestamp: string
  icon: string
  verb: string
  target_id: number | null
}

export interface ActivityItem {
  id: number
  user: string
  user_id: number | null
  timestamp: string
  action_text: string
  object_name: string | null
  icon: string
}

/**
 * Map verb_code to icon name for activity feed
 */
function mapVerbToIcon(verbCode: string): string {
  const iconMap: Record<string, string> = {
    'documents.document_create': 'upload',
    'documents.document_file_created': 'upload',
    'documents.document_download': 'download',
    'documents.document_file_downloaded': 'download',
    'documents.document_view': 'view',
    'documents.document_delete': 'delete',
    'documents.document_properties_edit': 'edit',
    'documents.document_metadata_added': 'tag',
    'documents.document_metadata_edited': 'tag',
    'documents.document_tag_attach': 'tag',
    'documents.document_tag_remove': 'tag',
    'cabinets.cabinet_document_add': 'collection',
    'cabinets.cabinet_document_remove': 'collection',
    'document_states.workflow_transition': 'status',
    'authentication.user_logged_in': 'login',
    'authentication.user_logged_out': 'logout',
  }
  return iconMap[verbCode] || 'info'
}

/**
 * Convert HeadlessActivityItem to ActivityItem format
 */
function mapHeadlessToActivityItem(item: HeadlessActivityItem): ActivityItem {
  return {
    id: item.id,
    user: item.actor?.username || 'system',
    user_id: item.actor?.id || null,
    timestamp: item.timestamp,
    action_text: item.verb || '',  // Уже переведенный текст
    object_name: item.target?.label || null,
    icon: mapVerbToIcon(item.verb_code || '')
  }
}

export async function getDashboardActivity(
  limit = 20
): Promise<DashboardActivityItem[]> {
  const url = `/api/v4/headless/dashboard/activity/?limit=${limit}`
  return apiService.get<DashboardActivityItem[]>(url)
}

/**
 * Get dashboard activity normalized for display
 * Automatically determines user role and applies appropriate filters
 */
export async function getDashboardActivityNormalized(
  limit = 10
): Promise<ActivityItem[]> {
  const { useAuthStore } = await import('@/stores/authStore')
  const authStore = useAuthStore()

  const user = authStore.user
  const isAdmin = Boolean(
    user && (
      user.is_staff === true ||
      user.is_superuser === true ||
      (user as any).can_access_admin_panel === true
    )
  )

  const filter = isAdmin ? 'all' : 'my_documents'
  const url = `/api/v4/headless/activity/feed/?filter=${filter}&important=1&system=0&page_size=${limit}`
  const response = await apiService.get<HeadlessActivityFeedResponse>(
    url,
    undefined,
    false
  )

  if (!response || !Array.isArray(response.results)) {
    throw new Error('Invalid response format from activity feed API')
  }

  return response.results.map(mapHeadlessToActivityItem)
}

