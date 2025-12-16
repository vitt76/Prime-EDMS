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
  try {
    // Import authStore dynamically to avoid circular dependencies
    const { useAuthStore } = await import('@/stores/authStore')
    const authStore = useAuthStore()
    
    // Determine user role from authStore
    const user = authStore.user
    const isAdmin = user && (
      user.is_staff === true || 
      user.is_superuser === true ||
      (user as any).can_access_admin_panel === true
    )
    
    // Select filter based on user role
    // 'all' - для админов (все события)
    // 'my_documents' - для пользователей (только доступные документы)
    const filter = isAdmin ? 'all' : 'my_documents'
    
    // Build URL with filters
    const url = `/api/v4/headless/activity/feed/?filter=${filter}&important=1&system=0&page_size=${limit}`
    
    if (import.meta.env.DEV) {
      console.log(`[ActivityService] Fetching activity feed: filter=${filter}, limit=${limit}, isAdmin=${isAdmin}`)
    }
    
    // Fetch data from HeadlessActivityFeedView
    const response = await apiService.get<HeadlessActivityFeedResponse>(
      url,
      undefined,
      false // Don't cache activity feed
    )
    
    // Validate response structure
    if (!response || !Array.isArray(response.results)) {
      console.warn('[ActivityService] Invalid response format:', response)
      throw new Error('Invalid response format from activity feed API')
    }
    
    // Map HeadlessActivityItem[] to ActivityItem[]
    return response.results.map(mapHeadlessToActivityItem)
    
  } catch (err) {
    console.warn('[ActivityService] Failed to fetch activity feed:', err)
    // Fallback: try old endpoint if new one fails
    try {
      const items = await getDashboardActivity(limit)
      return items.map((item) => ({
        id: item.id,
        user: item.user,
        user_id: item.user_id,
        timestamp: item.timestamp,
        action_text: item.action_text,
        object_name: item.object_name,
        icon: item.icon || 'upload'
      }))
    } catch (fallbackErr) {
      console.warn('[ActivityService] Fallback also failed:', fallbackErr)
      return []
    }
  }
}

