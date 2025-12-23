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

  const preferredFileId =
    asset?.selected_file_id ||
    asset?.current_file_id ||
    asset?.file_latest_id ||
    asset?.file_id ||
    asset?.file?.id

  const versionId =
    asset?.version_active_id ||
    asset?.version_id ||
    asset?.version?.id ||
    asset?.version_active?.id ||
    'latest'

  const filePreview =
    asset?.id && preferredFileId
      ? `/api/v4/documents/${asset.id}/files/${preferredFileId}/pages/1/image/?width=1200`
      : undefined

  const versionPreview =
    asset?.id && versionId
      ? `/api/v4/documents/${asset.id}/versions/${versionId}/pages/1/image/?width=1200`
      : undefined

  const fallbackPreview = filePreview || versionPreview

  const url =
    filePreview ||
    asset.thumbnail_url ||
    asset.preview_url ||
    asset.download_url ||
    fallbackPreview

  return makeAbsolute(url) || PLACEHOLDER
}

