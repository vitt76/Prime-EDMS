export const formatDate = (date: string | Date, locale: 'ru' | 'en' = 'ru'): string => {
  return new Date(date).toLocaleDateString(
    locale === 'ru' ? 'ru-RU' : 'en-US',
    { year: 'numeric', month: 'long', day: 'numeric' }
  )
}

export const formatRelativeTime = (date: string | Date, locale: 'ru' | 'en' = 'ru'): string => {
  const now = new Date()
  const then = new Date(date)
  const diffMs = now.getTime() - then.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return locale === 'ru' ? 'Сегодня' : 'Today'
  if (diffDays === 1) return locale === 'ru' ? 'Вчера' : 'Yesterday'
  if (diffDays < 7) return `${diffDays} ${locale === 'ru' ? 'дней назад' : 'days ago'}`

  return formatDate(date, locale)
}

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0
  }).format(amount)
}

export const formatNumber = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}
