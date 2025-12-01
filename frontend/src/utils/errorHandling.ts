/**
 * Extract a machine-readable error code from API errors.
 * Supports Axios response payloads with nested `error` objects.
 */
export function extractErrorCode(error: unknown): string | null {
  if (!error || typeof error !== 'object') {
    return null
  }

  const maybeError = error as Record<string, unknown>

  if (typeof maybeError.code === 'string') {
    return maybeError.code
  }

  const response = maybeError.response as Record<string, unknown> | undefined
  if (response) {
    const data = response.data as Record<string, unknown> | undefined
    if (data) {
      const nested = (data.error ?? data.errors) as Record<string, unknown> | undefined
      if (nested && typeof nested.code === 'string') {
        return nested.code
      }

      if (typeof data.code === 'string') {
        return data.code
      }
    }
  }

  return null
}

