import { z } from 'zod'

export const emailSchema = z.string().email('Invalid email format')

export const passwordSchema = z.string()
  .min(8, 'Minimum 8 characters')
  .regex(/[0-9]/, 'Must contain at least one number')
  .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Must contain at least one special character')

export const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  organization_name: z.string().min(2, 'Minimum 2 characters'),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  agree_terms: z.boolean().refine((value) => value === true, 'Must agree to terms')
})

export const contactSchema = z.object({
  name: z.string().min(2, 'Minimum 2 characters'),
  email: emailSchema,
  message: z.string().min(10, 'Minimum 10 characters')
})

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required')
})
