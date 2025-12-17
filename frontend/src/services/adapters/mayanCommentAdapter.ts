/**
 * Adapter for converting Mayan EDMS comment API responses to frontend Comment format
 */

import type { Comment } from '@/types/api'

/**
 * Response format from Mayan EDMS Comment API
 */
export interface MayanCommentResponse {
  id: number
  submit_date: string
  text: string
  url: string
  user: {
    id: number
    username: string
    first_name?: string
    last_name?: string
    email?: string
    url?: string
  }
}

/**
 * Convert Mayan EDMS comment response to frontend Comment format
 */
export function adaptMayanCommentToFrontend(mayanComment: MayanCommentResponse): Comment {
  const user = mayanComment.user
  const fullName = user.first_name && user.last_name
    ? `${user.first_name} ${user.last_name}`
    : user.first_name || user.last_name || user.username

  // Generate avatar URL using ui-avatars.com
  const authorName = encodeURIComponent(fullName)
  const authorAvatar = `https://ui-avatars.com/api/?name=${authorName}&background=6366f1&color=fff&size=128`

  return {
    id: mayanComment.id,
    author: fullName,
    author_id: user.id,
    author_avatar: authorAvatar,
    text: mayanComment.text,
    created_date: mayanComment.submit_date,
    // Mayan EDMS doesn't track edit date separately, so we can't determine if edited
    // We'll leave edited as undefined unless we add edit tracking later
    edited: false
  }
}

/**
 * Convert frontend comment request to Mayan EDMS API format
 */
export function adaptFrontendCommentToMayan(text: string): { text: string } {
  return {
    text: text.trim()
  }
}
