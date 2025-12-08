const API_BASE = (import.meta as any)?.env?.VITE_API_URL || 'http://localhost:8080'
const PLACEHOLDER = '/placeholder-document.svg'

function makeAbsolute(url: string | undefined | null): string | undefined {
  if (!url) return undefined
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return `${API_BASE}${url.startsWith('/') ? '' : '/'}${url}`
}

export function resolveAssetImageUrl(asset: any): string {
  if (!asset) return PLACEHOLDER

  const url =
    asset.thumbnail_url ||
    asset.preview_url ||
    asset.download_url ||
    (asset.id ? `/api/v4/documents/${asset.id}/versions/latest/pages/1/image/?width=1200` : undefined)

  return makeAbsolute(url) || PLACEHOLDER
}

