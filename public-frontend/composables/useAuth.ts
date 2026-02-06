import type { RegisterPayload, VerifyEmailPayload } from '~/types/auth'

export function useAuth() {
  const { register, verifyEmail } = useApi()

  return { register, verifyEmail }
}
