import { apiService } from './apiService'

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

export async function getDashboardActivity(
  limit = 20
): Promise<DashboardActivityItem[]> {
  const url = `/api/v4/headless/dashboard/activity/?limit=${limit}`
  return apiService.get<DashboardActivityItem[]>(url)
}

export async function getDashboardActivityNormalized(
  limit = 20
): Promise<ActivityItem[]> {
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
}

