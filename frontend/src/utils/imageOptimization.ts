/**
 * Image optimization utilities
 * Provides functions for generating WebP URLs and optimizing image loading
 */

/**
 * Generate WebP URL from original image URL
 * @param originalUrl - Original image URL
 * @returns WebP URL or undefined if conversion not possible
 */
export function getWebPUrl(originalUrl: string): string | undefined {
  if (!originalUrl) return undefined
  
  try {
    const url = new URL(originalUrl, window.location.origin)
    const pathname = url.pathname
    
    // Try to replace common image extensions with .webp
    const webpPath = pathname.replace(/\.(jpg|jpeg|png)$/i, '.webp')
    
    // Only return if path actually changed (extension was found)
    if (webpPath !== pathname) {
      return `${url.origin}${webpPath}${url.search}${url.hash}`
    }
  } catch {
    // If URL parsing fails, try simple string replacement
    return originalUrl.replace(/\.(jpg|jpeg|png)$/i, '.webp')
  }
  
  return undefined
}

/**
 * Generate responsive image srcset
 * @param baseUrl - Base image URL
 * @param sizes - Array of sizes (e.g., ['300w', '600w', '1200w'])
 * @returns srcset string
 */
export function generateSrcSet(baseUrl: string, sizes: string[]): string {
  return sizes
    .map((size) => {
      const width = size.replace('w', '')
      // Assuming backend supports size parameter
      return `${baseUrl}?w=${width} ${size}`
    })
    .join(', ')
}

/**
 * Get optimal image size based on viewport
 * @param viewportWidth - Current viewport width
 * @returns Recommended image width
 */
export function getOptimalImageSize(viewportWidth: number): number {
  if (viewportWidth >= 1280) return 1200 // xl
  if (viewportWidth >= 1024) return 800  // lg
  if (viewportWidth >= 768) return 600  // md
  if (viewportWidth >= 640) return 400   // sm
  return 300 // mobile
}

















