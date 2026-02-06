export interface RegisterPayload {
  email: string
  password: string
  organization_name: string
  first_name?: string
  last_name?: string
  phone?: string
  company_size?: string
  lang?: string
  agree_terms: boolean
}

export interface VerifyEmailPayload {
  token: string
}
