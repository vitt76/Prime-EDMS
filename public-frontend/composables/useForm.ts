import type { ZodSchema } from 'zod'

export function useForm<T extends Record<string, any>>(schema: ZodSchema<T>) {
  const errors = ref<Record<string, string>>({})

  const validate = (payload: T) => {
    const result = schema.safeParse(payload)
    errors.value = {}
    if (!result.success) {
      for (const issue of result.error.issues) {
        const key = issue.path.join('.') || 'form'
        errors.value[key] = issue.message
      }
      return null
    }
    return result.data
  }

  return { errors, validate }
}
