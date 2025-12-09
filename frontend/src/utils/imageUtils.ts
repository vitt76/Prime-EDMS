const API_BASE =
  (import.meta as any)?.env?.VITE_API_BASE_URL ||
  (import.meta as any)?.env?.VITE_API_URL ||
  'http://localhost:8000'

const PLACEHOLDER = '/placeholder-document.svg'

function makeAbsolute(url: string | undefined | null): string | undefined {
  if (!url) return undefined
  if (url.startsWith('data:image')) return url
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  // relative path -> prepend backend base
  return `${API_BASE}${url.startsWith('/') ? '' : '/'}${url}`
}

export function resolveAssetImageUrl(asset: any): string {
  if (!asset) return PLACEHOLDER

  const versionId =
    asset?.version_active_id ||
    asset?.version_id ||
    asset?.version?.id ||
    asset?.version_active?.id ||
    'latest'

  const fallbackPreview =
    asset?.id
      ? `/api/v4/documents/${asset.id}/versions/${versionId}/pages/1/image/?width=1200`
      : undefined

  const url =
    asset.thumbnail_url ||
    asset.preview_url ||
    asset.download_url ||
    fallbackPreview

  return makeAbsolute(url) || PLACEHOLDER
}

