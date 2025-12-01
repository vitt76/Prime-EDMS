export interface SharePermissions {
  view: boolean
  download: boolean
}

export interface ShareLink {
  id: number
  url: string
  token: string
  expires_at?: string
  password_protected: boolean
  permissions: SharePermissions
  created_date: string
}

export interface CreateSharePayload {
  permissions: SharePermissions
  expires_at?: string
  password?: string
  share_with_users?: string[]
}

