import { describe, it, expect } from 'vitest'
import { formatFileSize, formatDate, formatRelativeTime, truncate } from '@/utils/formatters'

describe('formatters', () => {
  describe('formatFileSize', () => {
    it('formats bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes')
      expect(formatFileSize(1024)).toBe('1 KB')
      expect(formatFileSize(1048576)).toBe('1 MB')
      expect(formatFileSize(1073741824)).toBe('1 GB')
    })
  })

  describe('formatDate', () => {
    it('formats date in short format', () => {
      const date = new Date('2025-11-25')
      const formatted = formatDate(date, 'short')
      expect(formatted).toMatch(/\d{2}\.\d{2}\.\d{4}/)
    })

    it('formats date in long format', () => {
      const date = new Date('2025-11-25T10:30:00')
      const formatted = formatDate(date, 'long')
      expect(formatted).toContain('2025')
    })
  })

  describe('formatRelativeTime', () => {
    it('formats recent time correctly', () => {
      const now = new Date()
      const oneMinuteAgo = new Date(now.getTime() - 60 * 1000)
      expect(formatRelativeTime(oneMinuteAgo)).toContain('мин.')
    })
  })

  describe('truncate', () => {
    it('truncates long text', () => {
      const longText = 'This is a very long text that needs to be truncated'
      expect(truncate(longText, 20)).toBe('This is a very long ...')
    })

    it('does not truncate short text', () => {
      const shortText = 'Short text'
      expect(truncate(shortText, 20)).toBe('Short text')
    })
  })
})


