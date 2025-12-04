# 🚀 Transformation & Merge Roadmap

## Vue 3 Frontend ↔ Django Backend Integration Plan

**Дата создания:** 03 декабря 2025
**Дата обновления:** 03 декабря 2025
**Версия:** 1.3 (Added B-Hotfix Phase - Critical Auth Blocker)
**Статус:** 🚨 BLOCKED by Backend Crash - Critical Auth Issue
**Команда:** Виталий (Frontend), Дмитрий (Backend)
**Blocker:** GET /api/v4/users/current/ returns 500 Internal Server Error

---

## 📋 Содержание

1. [High-Level Strategy](#1-high-level-strategy)
2. [Parallel Workstreams](#2-parallel-workstreams)
3. [Integration Points](#3-integration-points)
4. [Git Strategy](#4-git-strategy)
5. [Risk Management](#5-risk-management)
6. [Timeline & Milestones](#6-timeline--milestones)
7. [Definition of Done](#7-definition-of-done)

---

## 🚨 CRITICAL BLOCKER ALERT

**Status:** 🚨 **PROJECT BLOCKED** — Cannot proceed with Phase A-Fix

**Issue:** GET `/api/v4/users/current/` returns **500 Internal Server Error** due to S3/Serializer crashes

**Impact:** Frontend authentication flow completely broken. Login impossible.

**Solution:** **Phase B-Hotfix** must be completed first (Week 8-9).

**Next Steps:**
1. Backend team (Дмитрий): Implement B-Hotfix.1-3 this week
2. Test GET `/api/v4/users/current/` returns 200 OK
3. Resume Phase A-Fix (Week 10-11)

---

## 1. High-Level Strategy

### 1.1 Architectural Approach: Adapter Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER (Vue 3)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Pages     │  │ Components  │  │   Stores    │  │  Services   │         │
│  │  (Views)    │  │    (UI)     │  │  (Pinia)    │  │  (Axios)    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                │                 │
│         └────────────────┴────────────────┴────────────────┘                 │
│                                   │                                          │
│                          ┌────────▼────────┐                                 │
│                          │    ADAPTERS     │  ◄── NEW LAYER                  │
│                          │  (Data Mapping) │                                 │
│                          └────────┬────────┘                                 │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                           ┌────────▼────────┐
                           │  Vite Proxy     │  localhost:5173 → :8080
                           └────────┬────────┘
                                    │
┌───────────────────────────────────┼─────────────────────────────────────────┐
│                           BACKEND LAYER (Django)                             │
│                          ┌────────▼────────┐                                 │
│                          │   REST API      │                                 │
│                          │  (DRF 3.13.1)   │                                 │
│                          └────────┬────────┘                                 │
│         ┌─────────────────────────┼─────────────────────────┐                │
│         │                         │                         │                │
│  ┌──────▼──────┐          ┌───────▼───────┐         ┌───────▼───────┐       │
│  │ /api/v4/    │          │  /api/dam/    │         │ /api/v4/      │       │
│  │ documents/  │          │  (Custom DAM) │         │ search/       │       │
│  └─────────────┘          └───────────────┘         └───────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Ключевые принципы:**

1. **Frontend адаптируется к Backend** — не модифицируем core Mayan API без необходимости
2. **Adapter Pattern** — создаём слой преобразования данных между форматами
3. **Backend дополняет API** — создаём новые endpoints только для недостающего функционала
4. **Feature Flags** — позволяют постепенный переход с mock на real API

### 1.2 Feature Flag Strategy

```typescript
// frontend/.env.development
VITE_API_URL=http://localhost:8080
VITE_USE_REAL_API=false          # Phase 1: Mock mode (current)
VITE_USE_REAL_API=true           # Phase 2+: Real API mode

// frontend/.env.production
VITE_API_URL=                     # Same origin
VITE_USE_REAL_API=true           # Always real in production
```

**Реализация в коде:**

```typescript
// frontend/src/config/features.ts
export const FEATURES = {
  USE_REAL_API: import.meta.env.VITE_USE_REAL_API === 'true',
  ENABLE_AI_ANALYSIS: import.meta.env.VITE_ENABLE_AI === 'true',
  ENABLE_2FA: import.meta.env.VITE_ENABLE_2FA === 'true',
}

// Usage in services
export class AssetService {
  async getAssets(params: GetAssetsParams) {
    if (!FEATURES.USE_REAL_API) {
      return mockAssets  // Development fallback
    }
    return apiService.get('/api/v4/documents/', { params })
  }
}
```

### 1.3 API Contract Principles

| Principle | Description |
|-----------|-------------|
| **JSON-First** | Все endpoints возвращают `application/json` |
| **RESTful** | Следуем REST conventions (GET/POST/PUT/PATCH/DELETE) |
| **Paginated** | Списки всегда пагинированы (`{count, next, previous, results}`) |
| **Typed Responses** | Каждый endpoint документирован в OpenAPI/Swagger |
| **Error Codes** | Стандартизированные коды ошибок (`{error, error_code, detail}`) |

---

## 2. Parallel Workstreams

### 2.1 Overview: The Split

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEEK 1-2                                        │
│  ┌────────────────────────────┐    ┌────────────────────────────┐           │
│  │   STREAM A (Frontend)      │    │   STREAM B (Backend)       │           │
│  │   Assignee: Виталий        │    │   Assignee: Дмитрий        │           │
│  │                            │    │                            │           │
│  │   A1: Foundation           │◄──►│   B1: API Gap Fill         │           │
│  │   - Vite Proxy             │    │   - JSON Serializers       │           │
│  │   - Axios Interceptors     │    │   - TokenAuth Enable       │           │
│  │   - Auth Store (Token)     │    │   - CORS Config            │           │
│  └────────────────────────────┘    └────────────────────────────┘           │
│                     │                           │                            │
│                     ▼                           ▼                            │
│              ✅ CHECKPOINT #1: Auth Handshake                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEEK 3-4                                        │
│  ┌────────────────────────────┐    ┌────────────────────────────┐           │
│  │   A2: Read-Only Layer      │◄──►│   B2: Performance          │           │
│  │   - Document Adapter       │    │   - N+1 Query Fix          │           │
│  │   - Gallery View → API     │    │   - Search Optimization    │           │
│  │   - Asset Detail → API     │    │   - Thumbnail Cache        │           │
│  └────────────────────────────┘    └────────────────────────────┘           │
│                     │                           │                            │
│                     ▼                           ▼                            │
│              ✅ CHECKPOINT #2: Gallery Displays Real Data                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEEK 5-6                                        │
│  ┌────────────────────────────┐    ┌────────────────────────────┐           │
│  │   A3: Write Layer          │◄──►│   B3: S3 & Uploads         │           │
│  │   - Upload Service         │    │   - S3 Storage Test        │           │
│  │   - Metadata Forms         │    │   - Chunked Upload API     │           │
│  │   - Tag Management         │    │   - Bulk Operations API    │           │
│  └────────────────────────────┘    └────────────────────────────┘           │
│                     │                           │                            │
│                     ▼                           ▼                            │
│              ✅ CHECKPOINT #3: Full CRUD Operations Work                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEEK 7-8                                        │
│  ┌────────────────────────────┐    ┌────────────────────────────┐           │
│  │   A4: Admin UI             │◄──►│   B4: Async & Webhooks     │           │
│  │   - User Management        │    │   - AI Status Polling      │           │
│  │   - Metadata Schemas       │    │   - WebSocket Setup        │           │
│  │   - Workflow Designer      │    │   - Background Tasks       │           │
│  └────────────────────────────┘    └────────────────────────────┘           │
│                     │                           │                            │
│                     ▼                           ▼                            │
│              ✅ CHECKPOINT #4: Admin Panel Fully Functional                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                             WEEK 9-10                                       │
│  ┌────────────────────────────┐    ┌────────────────────────────┐           │
│  │   A-Fix: Integration       │◄──►│   B-Fix: Backend Stubs     │           │
│  │   Polish & Correction      │    │   - Missing Endpoints      │           │
│  │   - Upload Flow Fix        │    │   - Special Collections    │           │
│  │   - Mock Cleanup           │    │   - Activity Feed          │           │
│  │   - Download Layer         │    │   - Performance Tuning     │           │
│  └────────────────────────────┘    └────────────────────────────┘           │
│                     │                           │                            │
│                     ▼                           ▼                            │
│              🎯 CHECKPOINT #5: 100% Integration (No Mocks)                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Stream A: Frontend Integration (Виталий)

#### Phase A1: Foundation (Week 1-2)

**Goal:** Establish secure communication between Frontend and Backend.

##### A1.1 Vite Proxy Configuration

```typescript
// frontend/vite.config.ts — UPDATED
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: 'localhost',
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq) => {
            // Log requests in dev
            console.log(`[Proxy] ${proxyReq.method} ${proxyReq.path}`)
          })
        }
      },
      '/media': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
```

**Checklist:**
- [ ] Update `vite.config.ts` with proxy configuration
- [ ] Test proxy connectivity to backend
- [ ] Verify CSRF token flow
- [ ] Add request logging for debugging

##### A1.2 Axios Interceptors

```typescript
// frontend/src/services/apiService.ts — UPDATED
class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '',
      timeout: 30000,
      withCredentials: true,  // Important for session cookies
    })
    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use((config) => {
      // Add CSRF token from cookie or meta tag
      const csrfToken = this.getCSRFToken()
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      }
      
      // Add Auth token if available
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers['Authorization'] = `Token ${token}`
      }
      
      return config
    })

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired - redirect to login
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  private getCSRFToken(): string | null {
    // Try cookie first
    const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/)
    if (cookieMatch) return cookieMatch[1]
    
    // Fallback to meta tag
    return document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content || null
  }
}
```

**Checklist:**
- [ ] Implement CSRF token extraction
- [ ] Add Authorization header with Token
- [ ] Implement 401 handling (redirect to login)
- [ ] Add retry logic for 5xx errors
- [ ] Test with real backend

##### A1.3 Auth Store Refactor

```typescript
// frontend/src/stores/authStore.ts — UPDATED
export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const permissions = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Actions
  async function login(username: string, password: string) {
    isLoading.value = true
    error.value = null
    
    try {
      // Step 1: Get token
      const tokenResponse = await authService.obtainToken(username, password)
      token.value = tokenResponse.token
      localStorage.setItem('auth_token', tokenResponse.token)
      
      // Step 2: Get user info
      const userResponse = await authService.getCurrentUser()
      user.value = userResponse
      permissions.value = userResponse.permissions || []
      
      return { success: true }
    } catch (err) {
      error.value = formatApiError(err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await authService.logout()
    } finally {
      // Always clear local state
      token.value = null
      user.value = null
      permissions.value = []
      localStorage.removeItem('auth_token')
    }
  }

  async function checkAuth() {
    if (!token.value) return false
    
    try {
      const userResponse = await authService.getCurrentUser()
      user.value = userResponse
      permissions.value = userResponse.permissions || []
      return true
    } catch {
      await logout()
      return false
    }
  }

  return {
    user, token, permissions, isLoading, error,
    isAuthenticated,
    login, logout, checkAuth
  }
}, {
  persist: {
    paths: ['token']  // Only persist token, not user data
  }
})
```

**Checklist:**
- [ ] Remove `useMock` from persist paths in `assetStore`
- [ ] Implement Token-based auth flow
- [ ] Add `checkAuth()` on app initialization
- [ ] Fix `LoginPage.vue` input type (`email` → `text`)
- [ ] Test login/logout flow with real backend

##### A1.4 Auth Service

```typescript
// frontend/src/services/authService.ts — UPDATED
class AuthService {
  /**
   * Obtain auth token from backend
   */
  async obtainToken(username: string, password: string): Promise<{ token: string }> {
    const response = await apiService.post<{ token: string }>(
      '/api/v4/auth/token/obtain/',
      { username, password }
    )
    return response
  }

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    return apiService.get<User>('/api/v4/user_management/users/current/')
  }

  /**
   * Logout (invalidate session)
   */
  async logout(): Promise<void> {
    await apiService.post('/api/v4/auth/logout/')
  }
}

export const authService = new AuthService()
```

**Checklist:**
- [ ] Update endpoint URLs to match backend
- [ ] Add error handling for invalid credentials
- [ ] Test with real backend credentials

---

#### Phase A2: Read-Only Layer (Week 3-4)

**Goal:** Display real documents from backend in Gallery.

##### A2.1 Document Adapter

```typescript
// frontend/src/services/adapters/documentAdapter.ts — NEW FILE
import type { Asset, AIAnalysis } from '@/types/api'

/**
 * Mayan EDMS Document response structure
 */
interface MayanDocument {
  id: number
  uuid: string
  label: string
  description: string
  datetime_created: string
  language: string
  document_type: {
    id: number
    label: string
  }
  file_latest?: {
    id: number
    filename: string
    mimetype: string
    size: number
    timestamp: string
    checksum: string
    download_url: string
    page_count: number
  }
  version_active?: {
    id: number
    timestamp: string
  }
  // DAM Extension fields (from /api/dam/document-detail/)
  ai_analysis?: {
    ai_description: string | null
    ai_tags: string[] | null
    dominant_colors: Array<{hex: string; name: string; percentage: number}> | null
    categories: string[] | null
    people: string[] | null
    locations: string[] | null
    analysis_status: 'pending' | 'processing' | 'completed' | 'failed'
    ai_provider: string | null
    analysis_completed: string | null
  }
  tags?: Array<{ id: number; label: string; color: string }>
  metadata?: Array<{ id: number; metadata_type: { name: string }; value: string }>
}

/**
 * Maps Mayan EDMS Document to Frontend Asset type
 */
export function adaptMayanDocument(doc: MayanDocument): Asset {
  const file = doc.file_latest
  
  return {
    id: doc.id,
    label: doc.label,
    filename: file?.filename || doc.label,
    size: file?.size || 0,
    mime_type: file?.mimetype || 'application/octet-stream',
    date_added: doc.datetime_created,
    
    // Generate thumbnail/preview URLs
    thumbnail_url: file 
      ? `/api/v4/documents/${doc.id}/versions/latest/pages/1/image/?width=150&height=150`
      : undefined,
    preview_url: file
      ? `/api/v4/documents/${doc.id}/versions/latest/pages/1/image/?width=800`
      : undefined,
    
    // Tags
    tags: doc.tags?.map(t => t.label) || [],
    
    // Metadata as key-value
    metadata: doc.metadata?.reduce((acc, m) => {
      acc[m.metadata_type.name] = m.value
      return acc
    }, {} as Record<string, string>) || {},
    
    // AI Analysis
    ai_analysis: doc.ai_analysis ? adaptAIAnalysis(doc.ai_analysis) : undefined,
    
    // Access level (from document type or ACL)
    access_level: 'private'
  }
}

/**
 * Maps DAM AI Analysis to Frontend AIAnalysis type
 */
function adaptAIAnalysis(analysis: MayanDocument['ai_analysis']): AIAnalysis | undefined {
  if (!analysis) return undefined
  
  return {
    tags: analysis.ai_tags || undefined,
    status: analysis.analysis_status,
    ai_description: analysis.ai_description || undefined,
    colors: analysis.dominant_colors?.map(c => c.hex) || undefined,
    provider: analysis.ai_provider || undefined,
    confidence: undefined  // Not provided by backend
  }
}

/**
 * Maps Frontend Asset back to Mayan Document update payload
 */
export function adaptAssetToDocument(asset: Partial<Asset>): Partial<MayanDocument> {
  return {
    label: asset.label,
    description: asset.metadata?.['description'] as string | undefined
  }
}
```

**Checklist:**
- [ ] Create `adapters/` directory
- [ ] Implement `documentAdapter.ts`
- [ ] Add unit tests for adapter
- [ ] Handle edge cases (missing fields)

##### A2.2 Asset Service Refactor

```typescript
// frontend/src/services/assetService.ts — UPDATED
import { adaptMayanDocument, adaptAssetToDocument } from './adapters/documentAdapter'
import type { Asset, PaginatedResponse, GetAssetsParams } from '@/types/api'

class AssetService {
  /**
   * Get paginated list of assets (documents)
   */
  async getAssets(params?: GetAssetsParams): Promise<PaginatedResponse<Asset>> {
    // Build query params for Mayan API
    const queryParams: Record<string, string | number> = {}
    
    if (params?.page) queryParams.page = params.page
    if (params?.page_size) queryParams.page_size = params.page_size
    if (params?.sort) queryParams.ordering = params.sort
    if (params?.search) queryParams.search = params.search
    if (params?.type) queryParams.document_type__label = params.type
    
    // Call Mayan Documents API
    const response = await apiService.get<MayanPaginatedResponse>(
      '/api/v4/documents/',
      { params: queryParams }
    )
    
    // Transform response using adapter
    return {
      count: response.count,
      next: response.next,
      previous: response.previous,
      results: response.results.map(adaptMayanDocument)
    }
  }

  /**
   * Get single asset with full details
   */
  async getAsset(id: number): Promise<Asset> {
    // Use DAM endpoint for enriched data (AI analysis, etc.)
    const doc = await apiService.get<MayanDocument>(
      `/api/dam/document-detail/${id}/`
    )
    return adaptMayanDocument(doc)
  }

  /**
   * Update asset metadata
   */
  async updateAsset(id: number, data: Partial<Asset>): Promise<Asset> {
    const payload = adaptAssetToDocument(data)
    const doc = await apiService.patch<MayanDocument>(
      `/api/v4/documents/${id}/`,
      payload
    )
    return adaptMayanDocument(doc)
  }

  /**
   * Delete asset (move to trash)
   */
  async deleteAsset(id: number): Promise<void> {
    await apiService.delete(`/api/v4/documents/${id}/`)
  }

  /**
   * Search assets
   */
  async searchAssets(query: string, params?: GetAssetsParams): Promise<PaginatedResponse<Asset>> {
    return this.getAssets({ ...params, search: query })
  }
}

export const assetService = new AssetService()
```

**Checklist:**
- [ ] Update `assetService.ts` endpoints
- [ ] Remove `/v4/dam/assets/` references
- [ ] Use `/api/v4/documents/` for list
- [ ] Use `/api/dam/document-detail/` for details
- [ ] Test pagination
- [ ] Test search functionality

##### A2.3 Gallery Store Update

```typescript
// frontend/src/stores/galleryStore.ts — UPDATE fetchAssets action
async function loadItems(page = 1) {
  if (isLoading.value) return
  
  isLoading.value = true
  error.value = null
  
  try {
    const response = await assetService.getAssets({
      page,
      page_size: pageSize.value,
      sort: sort.value.field,
      search: searchQuery.value || undefined,
      type: filters.value.type || undefined
    })
    
    if (page === 1) {
      items.value = response.results
      loadedPages.value.clear()
    } else {
      items.value.push(...response.results)
    }
    
    loadedPages.value.add(page)
    totalCount.value = response.count
    hasMore.value = !!response.next
    currentPage.value = page
    
  } catch (err) {
    error.value = formatApiError(err)
    console.error('[GalleryStore] Failed to load items:', err)
  } finally {
    isLoading.value = false
  }
}
```

**Checklist:**
- [ ] Remove mock data fallback from `galleryStore`
- [ ] Update `loadItems()` to use real API
- [ ] Test Gallery view with real data
- [ ] Verify thumbnails load correctly
- [ ] Test infinite scroll / pagination

##### A2.4 Asset Detail Page

**Checklist:**
- [ ] Update `AssetDetailPage.vue` to fetch real data
- [ ] Display AI analysis data
- [ ] Show metadata fields
- [ ] Test image/video preview
- [ ] Test download functionality

---

#### Phase A3: Write Layer (Week 5-6)

**Goal:** Enable document uploads and metadata editing.

##### A3.1 Upload Service (Two-Step Process)

```typescript
// frontend/src/services/uploadService.ts — UPDATED
class UploadService {
  /**
   * Upload document using Mayan's two-step process:
   * 1. Create document stub
   * 2. Upload file to the document
   */
  async uploadDocument(
    file: File,
    options: {
      label?: string
      documentTypeId?: number
      description?: string
      onProgress?: (progress: number) => void
    } = {}
  ): Promise<Asset> {
    // Step 1: Create document stub
    const documentResponse = await apiService.post<MayanDocument>(
      '/api/v4/documents/',
      {
        label: options.label || file.name,
        document_type_id: options.documentTypeId || 1,  // Default type
        description: options.description || ''
      }
    )
    
    const documentId = documentResponse.id
    
    // Step 2: Upload file to document
    const formData = new FormData()
    formData.append('file', file)
    formData.append('filename', file.name)
    
    await apiService.post(
      `/api/v4/documents/${documentId}/files/`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (event) => {
          if (options.onProgress && event.total) {
            const progress = Math.round((event.loaded / event.total) * 100)
            options.onProgress(progress)
          }
        }
      }
    )
    
    // Step 3: Fetch complete document with file info
    const completeDoc = await apiService.get<MayanDocument>(
      `/api/v4/documents/${documentId}/`
    )
    
    return adaptMayanDocument(completeDoc)
  }

  /**
   * Upload multiple files
   */
  async uploadDocuments(
    files: File[],
    options: {
      onFileProgress?: (index: number, progress: number) => void
      onFileComplete?: (index: number, asset: Asset) => void
    } = {}
  ): Promise<Asset[]> {
    const results: Asset[] = []
    
    for (let i = 0; i < files.length; i++) {
      const asset = await this.uploadDocument(files[i], {
        onProgress: (progress) => options.onFileProgress?.(i, progress)
      })
      results.push(asset)
      options.onFileComplete?.(i, asset)
    }
    
    return results
  }
}

export const uploadService = new UploadService()
```

**Checklist:**
- [ ] Implement two-step upload process
- [ ] Add progress tracking
- [ ] Handle upload errors gracefully
- [ ] Test with various file types
- [ ] Test large file uploads
- [ ] Update `UploadStep.vue` to use new service

##### A3.2 Metadata Editing

```typescript
// frontend/src/services/metadataService.ts — UPDATE
class MetadataService {
  /**
   * Get document metadata
   */
  async getDocumentMetadata(documentId: number): Promise<DocumentMetadata[]> {
    const response = await apiService.get<{ results: DocumentMetadata[] }>(
      `/api/v4/documents/${documentId}/metadata/`
    )
    return response.results
  }

  /**
   * Add metadata to document
   */
  async addMetadata(
    documentId: number,
    metadataTypeId: number,
    value: string
  ): Promise<DocumentMetadata> {
    return apiService.post(
      `/api/v4/documents/${documentId}/metadata/`,
      { metadata_type_id: metadataTypeId, value }
    )
  }

  /**
   * Update metadata value
   */
  async updateMetadata(
    documentId: number,
    metadataId: number,
    value: string
  ): Promise<DocumentMetadata> {
    return apiService.patch(
      `/api/v4/documents/${documentId}/metadata/${metadataId}/`,
      { value }
    )
  }

  /**
   * Remove metadata from document
   */
  async removeMetadata(documentId: number, metadataId: number): Promise<void> {
    await apiService.delete(
      `/api/v4/documents/${documentId}/metadata/${metadataId}/`
    )
  }
}

export const metadataService = new MetadataService()
```

**Checklist:**
- [ ] Implement metadata CRUD operations
- [ ] Update `EditMetadataModal.vue`
- [ ] Test adding/editing metadata
- [ ] Test removing metadata

##### A3.3 Tag Management

```typescript
// frontend/src/services/tagService.ts — NEW
class TagService {
  /**
   * Get all tags
   */
  async getTags(): Promise<Tag[]> {
    const response = await apiService.get<{ results: Tag[] }>('/api/v4/tags/')
    return response.results
  }

  /**
   * Get document tags
   */
  async getDocumentTags(documentId: number): Promise<Tag[]> {
    const response = await apiService.get<{ results: Tag[] }>(
      `/api/v4/documents/${documentId}/tags/`
    )
    return response.results
  }

  /**
   * Add tag to document
   */
  async addTagToDocument(documentId: number, tagId: number): Promise<void> {
    await apiService.post(`/api/v4/documents/${documentId}/tags/`, {
      tag_id: tagId
    })
  }

  /**
   * Remove tag from document
   */
  async removeTagFromDocument(documentId: number, tagId: number): Promise<void> {
    await apiService.delete(`/api/v4/documents/${documentId}/tags/${tagId}/`)
  }

  /**
   * Create new tag
   */
  async createTag(label: string, color: string): Promise<Tag> {
    return apiService.post('/api/v4/tags/', { label, color })
  }
}

export const tagService = new TagService()
```

**Checklist:**
- [ ] Implement tag service
- [ ] Update `TagInput.vue` component
- [ ] Test tag autocomplete
- [ ] Test adding/removing tags

---

#### Phase A4: Admin UI (Week 7-8)

**Goal:** Connect Admin panel to real backend APIs.

##### A4.1 User Management

**Checklist:**
- [ ] Connect `AdminUsers.vue` to `/api/v4/users/`
- [ ] Implement user creation
- [ ] Implement user editing
- [ ] Implement user deletion
- [ ] Test role assignment

##### A4.2 Group Management

**Checklist:**
- [ ] Connect to `/api/v4/groups/`
- [ ] Implement group CRUD
- [ ] Test permission assignment

##### A4.3 Metadata Schema Management

**Checklist:**
- [ ] Connect to `/api/v4/metadata_types/`
- [ ] Implement schema creation
- [ ] Test document type association

##### A4.4 Workflow Designer

**Checklist:**
- [ ] Connect to `/api/v4/workflows/`
- [ ] Implement workflow state management
- [ ] Test transition rules

---

#### Phase A-Fix: Integration Polish & Correction (Week 9-10)

**Goal:** Achieve 100% integration by fixing critical gaps and removing mock dependencies.

##### A-Fix.1: Critical Corrections (Priority 1)

**Fix Upload Architecture:**

**Technical Specification:**
"Refactor uploadWorkflowStore to use ChunkedUploadService. Ensure File.slice() is used for chunks. Handle 413 Payload Too Large gracefully."

```typescript
// frontend/src/stores/uploadWorkflowStore.ts — CRITICAL FIX
// REMOVE: Mock setTimeout logic
// REPLACE: Real ChunkedUploadService integration

class UploadWorkflowStore {
  async uploadFiles(files: File[]) {
    for (const file of files) {
      try {
        // ✅ Use ChunkedUploadService with File.slice() for chunks
        const uploadId = await this.initializeChunkedUpload(file)

        // Slice file into chunks using File.slice()
        const chunks = this.sliceFileIntoChunks(file)
        for (let i = 0; i < chunks.length; i++) {
          await this.uploadChunk(uploadId, chunks[i], i + 1, file.size)
          this.updateProgress(file.id, ((i + 1) / chunks.length) * 100)
        }

        // Complete upload and create document
        const asset = await this.completeChunkedUpload(uploadId, file.name)
        this.addUploadedAsset(asset)

      } catch (error) {
        // ✅ Handle 413 Payload Too Large gracefully
        if (error.response?.status === 413) {
          this.handlePayloadTooLarge(file, error)
        } else {
          this.handleUploadError(file, error)
        }
      }
    }
  }

  private sliceFileIntoChunks(file: File): Blob[] {
    const chunkSize = 5 * 1024 * 1024 // 5MB chunks
    const chunks: Blob[] = []
    for (let offset = 0; offset < file.size; offset += chunkSize) {
      const chunk = file.slice(offset, offset + chunkSize)
      chunks.push(chunk)
    }
    return chunks
  }

  // ✅ Ensure real progress bars work
  private updateProgress(fileId: string, progress: number) {
    const file = this.files.find(f => f.id === fileId)
    if (file) {
      file.uploadProgress = progress
      file.uploadStatus = progress === 100 ? 'completed' : 'uploading'
    }
  }
}
```

**Validation Criteria:**
"Upload a 200MB video file. Verify network tab shows multiple POST /append/ requests. Verify file appears in S3 bucket."

**Checklist:**
- [ ] Refactor `uploadWorkflowStore.ts` to use `ChunkedUploadService`
- [ ] Implement `File.slice()` for chunking logic
- [ ] Add 413 "Payload Too Large" error handling with user feedback
- [ ] Remove all `setTimeout` mock logic
- [ ] Test chunked upload with 200MB+ files
- [ ] Verify network requests: `POST /api/v4/uploads/init/`, multiple `POST /api/v4/uploads/append/`, `POST /api/v4/uploads/complete/`
- [ ] Confirm uploaded files appear in S3 bucket with correct paths

**Fix Data Persistence:**

```typescript
// frontend/src/stores/assetStore.ts — CRITICAL FIX
// REMOVE: useMock from persist paths

export const useAssetStore = defineStore('asset', () => {
  // ... state ...

  return {
    // ... actions ...
  }
}, {
  persist: {
    paths: ['filters', 'viewMode', 'sortBy']  // ❌ REMOVE 'useMock'
  }
})
```

**Checklist:**
- [ ] Remove `'useMock'` from all Pinia persist paths
- [ ] Audit all stores for mock-related persistence
- [ ] Ensure `VITE_USE_MOCK_DATA` env var is only source of truth
- [ ] Clear localStorage for all stores in dev environment
- [ ] Test that users cannot get stuck in mock mode

**Implement Download Layer:**

**Technical Specification:**
"Implement DownloadService.download(asset). Logic: Fetch document.file_latest.download_url. Create a hidden <a> tag with href=url and download attribute. If URL is not presigned, fallback to window.open()."

```typescript
// frontend/src/services/downloadService.ts — NEW FILE

class DownloadService {
  /**
   * Download single asset using presigned S3 URL
   */
  async downloadAsset(asset: Asset): Promise<void> {
    if (!asset.download_url) {
      // Fallback: Try to get download URL from asset metadata
      const downloadUrl = await this.getDownloadUrl(asset)
      if (!downloadUrl) {
        throw new Error('Asset has no download URL available')
      }
      asset.download_url = downloadUrl
    }

    try {
      // ✅ Primary: Use hidden <a> tag for direct download
      const link = document.createElement('a')
      link.href = asset.download_url
      link.download = asset.filename || asset.label
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      // ✅ Fallback: window.open() for non-presigned URLs
      console.warn('Direct download failed, using fallback:', error)
      window.open(asset.download_url, '_blank')
    }
  }

  /**
   * Get download URL from asset metadata or API
   */
  private async getDownloadUrl(asset: Asset): Promise<string | null> {
    // Try asset metadata first
    if (asset.file_details?.download_url) {
      return asset.file_details.download_url
    }

    // Fallback: Construct Mayan download URL
    // Note: This requires auth headers, handled by apiService
    return `/api/v4/documents/${asset.id}/files/latest/download/`
  }

  async downloadAssets(assets: Asset[]): Promise<void> {
    // Sequential download to prevent browser blocking
    for (const asset of assets) {
      await this.downloadAsset(asset)
      // Add delay to prevent overwhelming the browser
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  }
}

export const downloadService = new DownloadService()
```

**Validation Criteria:**
"Click 'Download' on an image. Browser starts downloading (not opening in new tab). Filename matches the asset label."

**Checklist:**
- [ ] Create `downloadService.ts` with `<a>` tag download logic
- [ ] Implement fallback to `window.open()` for non-presigned URLs
- [ ] Add download URL resolution from asset metadata
- [ ] Wire up "Download" buttons in `GalleryView.vue`
- [ ] Wire up "Download" buttons in `AssetDetailPage.vue`
- [ ] Implement bulk download with sequential processing
- [ ] Test download filename matches `asset.filename`
- [ ] Verify browser download prompt (not new tab)
- [ ] Test with expired presigned URLs (fallback works)
- [ ] Handle download errors with user feedback

##### A-Fix.2: Missing Integrations (Priority 2)

**Special Collections Integration:**

**Technical Specification:**
"If backend endpoints are missing, implement a temporary frontend filter (e.g., Favorites = LocalStore IDs). Mark as 'Temporary Tech Debt' until Stream B adds the endpoint."

```typescript
// frontend/src/pages/collections/FavoritesPage.vue — UPDATE
// TEMPORARY TECH DEBT: Frontend filter until backend endpoints ready

import { useLocalFavoritesStore } from '@/stores/localFavoritesStore'

async function fetchFavorites(page: number = 1, append: boolean = false) {
  isLoading.value = true

  try {
    // ✅ TEMPORARY: Use localStorage favorites until backend endpoint
    const favoriteIds = useLocalFavoritesStore().favoriteIds

    if (favoriteIds.length === 0) {
      assets.value = []
      totalCount.value = 0
      hasMore.value = false
      return
    }

    // Fetch assets by IDs (temporary solution)
    const response = await assetService.getAssetsByIds(favoriteIds, {
      page,
      page_size: pageSize.value
    })

    if (append) {
      assets.value = [...assets.value, ...response.results]
    } else {
      assets.value = response.results
    }

    totalCount.value = response.count
    hasMore.value = !!response.next

    // TODO: Replace with real backend endpoint
    // const response = await collectionsService.getFavorites({ page, page_size: pageSize.value })

  } catch (error) {
    console.error('Failed to fetch favorites:', error)
    // Fallback to empty state
    assets.value = []
    totalCount.value = 0
  } finally {
    isLoading.value = false
  }
}

// frontend/src/stores/localFavoritesStore.ts — TEMPORARY
export const useLocalFavoritesStore = defineStore('localFavorites', () => {
  const favoriteIds = ref<string[]>([])

  const addFavorite = (assetId: string) => {
    if (!favoriteIds.value.includes(assetId)) {
      favoriteIds.value.push(assetId)
    }
  }

  const removeFavorite = (assetId: string) => {
    favoriteIds.value = favoriteIds.value.filter(id => id !== assetId)
  }

  const isFavorite = (assetId: string): boolean => {
    return favoriteIds.value.includes(assetId)
  }

  return {
    favoriteIds,
    addFavorite,
    removeFavorite,
    isFavorite
  }
}, {
  persist: {
    paths: ['favoriteIds']
  }
})
```

**Checklist:**
- [ ] Implement temporary `localFavoritesStore` for favorites persistence
- [ ] Create `assetService.getAssetsByIds()` for bulk ID fetching
- [ ] Connect Favorites page to local favorites store
- [ ] Connect Recent page to local recent access tracking
- [ ] Connect MyUploads to user-specific filtering
- [ ] Connect SharedWithMe to shared document filtering
- [ ] **Mark as TEMPORARY TECH DEBT** with TODO comments
- [ ] Coordinate with Backend team for real endpoint implementation
- [ ] Test all special collection views with temporary solutions

**Dashboard Widgets Integration:**

**Activity Feed Technical Specification:**
"If no real endpoint exists, implement a ActivityLogService that records local user actions (Upload, Edit) to sessionStorage for the session demo. Do NOT leave hardcoded mocks."

```typescript
// frontend/src/services/activityLogService.ts — NEW FILE

interface ActivityLogEntry {
  id: string
  type: 'upload' | 'download' | 'edit' | 'delete' | 'share'
  asset_id?: number
  asset_label?: string
  timestamp: number
  details?: string
}

class ActivityLogService {
  private readonly STORAGE_KEY = 'activity_log'
  private readonly MAX_ENTRIES = 50

  /**
   * Log user activity for this session
   */
  logActivity(entry: Omit<ActivityLogEntry, 'id' | 'timestamp'>): void {
    const activities = this.getActivities()
    const newEntry: ActivityLogEntry = {
      ...entry,
      id: crypto.randomUUID(),
      timestamp: Date.now()
    }

    activities.unshift(newEntry) // Add to beginning

    // Keep only recent entries
    if (activities.length > this.MAX_ENTRIES) {
      activities.splice(this.MAX_ENTRIES)
    }

    sessionStorage.setItem(this.STORAGE_KEY, JSON.stringify(activities))
  }

  /**
   * Get recent activities for this session
   */
  getActivities(limit: number = 20): ActivityLogEntry[] {
    try {
      const stored = sessionStorage.getItem(this.STORAGE_KEY)
      if (!stored) return []

      const activities: ActivityLogEntry[] = JSON.parse(stored)
      return activities.slice(0, limit)
    } catch {
      return []
    }
  }

  /**
   * Clear all activities (for testing)
   */
  clearActivities(): void {
    sessionStorage.removeItem(this.STORAGE_KEY)
  }
}

export const activityLogService = new ActivityLogService()

// frontend/src/services/dashboardService.ts — UPDATE
// REMOVE: Mock activity data
// REPLACE: ActivityLogService for session-based logging

async getActivityFeed(): Promise<ActivityItem[]> {
  // ✅ TEMPORARY: Use session activity log until backend endpoint
  const activities = activityLogService.getActivities()

  return activities.map(activity => ({
    id: activity.id,
    type: activity.type,
    user: 'Current User', // TODO: Get from auth store
    user_id: 1, // TODO: Get from auth store
    asset_id: activity.asset_id,
    asset_label: activity.asset_label,
    timestamp: new Date(activity.timestamp).toISOString(),
    description: this.formatActivityDescription(activity)
  }))

  // TODO: Replace with real backend endpoint
  // return apiService.get('/api/v4/dam/activity/')
}

private formatActivityDescription(activity: ActivityLogEntry): string {
  const asset = activity.asset_label ? `"${activity.asset_label}"` : 'asset'

  switch (activity.type) {
    case 'upload': return `Uploaded ${asset}`
    case 'download': return `Downloaded ${asset}`
    case 'edit': return `Edited metadata for ${asset}`
    case 'delete': return `Deleted ${asset}`
    case 'share': return `Shared ${asset}`
    default: return `Performed action on ${asset}`
  }
}

async getStorageMetrics(): Promise<StorageMetrics> {
  // ✅ Use real storage endpoint (from B-Fix phase)
  return apiService.get('/api/dam/storage-metrics/')
}
```

**Checklist:**
- [ ] Create `ActivityLogService` for session-based activity logging
- [ ] Implement activity logging hooks in upload, edit, delete actions
- [ ] Connect Activity Feed to `activityLogService.getActivities()`
- [ ] Connect Storage Metrics to real backend endpoint
- [ ] Update DashboardPage to use activity log data
- [ ] Add activity logging to all major user actions
- [ ] **Mark as TEMPORARY until real backend endpoint**
- [ ] Test activity feed shows recent user actions
- [ ] Clear activities on logout for privacy

**Settings & Profile Forms:**

```typescript
// frontend/src/pages/SettingsPage.vue — UPDATE
// REMOVE: Mock profile update
// REPLACE: Real API calls

async function updateProfile(profileData: UserProfile) {
  try {
    // ✅ Use real profile update endpoint
    await authService.updateProfile(profileData)
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Profile updated successfully'
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to update profile'
    })
  }
}

async function changePassword(passwordData: ChangePasswordRequest) {
  try {
    // ✅ Use real password change endpoint
    await authService.changePassword(passwordData)
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Password changed successfully'
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to change password'
    })
  }
}
```

**Checklist:**
- [ ] Implement profile update form with real API
- [ ] Implement password change form with real API
- [ ] Add proper validation and error handling
- [ ] Test all settings forms
- [ ] Update backend endpoints if needed

##### A-Fix.3: Final Polish (Priority 3)

**Delete Mocks:**

```bash
# frontend/ — CLEANUP
# REMOVE: /src/mocks/ directory (keep only for dev/test if needed)
# KEEP: S3 fallback maps for development thumbnails

# Checklist:
- [ ] Remove /src/mocks/assets.ts
- [ ] Remove /src/mocks/folders.ts
- [ ] Remove /src/mocks/publications.ts
- [ ] Remove /src/mocks/workflows.ts
- [ ] Remove /src/mocks/metadata.ts
- [ ] Remove /src/mocks/ai.ts
- [ ] Remove /src/mocks/search.ts
- [ ] Keep /src/mocks/s3Provider.ts (for dev thumbnails)
- [ ] Keep /src/mocks/s3_map.json (for dev thumbnails)
```

**Lint & Cleanup:**

```typescript
// REMOVE: TODO comments related to mock data
// Examples to clean up:

// ❌ REMOVE THIS:
// frontend/src/stores/assetStore.ts
// TODO: Replace with real API when backend ready

// ✅ KEEP THIS (if still relevant):
// frontend/src/components/GalleryView.vue
// TODO: Implement virtual scrolling for 1000+ items
```

**Checklist:**
- [ ] Remove mock-related TODO comments
- [ ] Clean up console.log statements from development
- [ ] Remove unused mock imports
- [ ] Run full lint check
- [ ] Fix any TypeScript errors from cleanup

**Environment Verification:**

```typescript
// frontend/src/config/env.ts — VERIFY
export const ENV = {
  API_URL: import.meta.env.VITE_API_URL || '',
  USE_REAL_API: import.meta.env.VITE_USE_REAL_API === 'true',
  ENABLE_AI: import.meta.env.VITE_ENABLE_AI === 'true',
  ENABLE_2FA: import.meta.env.VITE_ENABLE_2FA === 'true',
}

// VERIFY: All services use ENV.API_URL consistently
// VERIFY: No hardcoded 'http://localhost:8080' in production code
```

**Checklist:**
- [ ] Verify all services use `ENV.API_URL`
- [ ] Check for hardcoded URLs in production code
- [ ] Test with different environment configurations
- [ ] Ensure proper fallback for missing env vars
- [ ] Document environment setup in README

---

### 2.3 Stream B: Backend Adaptation (Дмитрий)

#### Phase B1: API Gap Fill (Week 1-2)

**Goal:** Ensure all required endpoints return proper JSON.

##### B1.1 JSON Serializers

```python
# mayan/apps/dam/serializers.py — VERIFY/UPDATE

class DAMDocumentDetailSerializer(serializers.Serializer):
    """
    Enriched document serializer with DAM-specific fields.
    Returns pure JSON (no HTML).
    """
    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    label = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    datetime_created = serializers.DateTimeField(read_only=True)
    language = serializers.CharField()
    
    document_type = DocumentTypeSerializer(read_only=True)
    file_latest = DocumentFileSerializer(read_only=True)
    
    # DAM Extension
    ai_analysis = DocumentAIAnalysisSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    metadata = DocumentMetadataSerializer(many=True, read_only=True)
    
    # Computed fields
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    def get_thumbnail_url(self, obj):
        return f'/api/v4/documents/{obj.id}/versions/latest/pages/1/image/?width=150&height=150'
    
    def get_preview_url(self, obj):
        return f'/api/v4/documents/{obj.id}/versions/latest/pages/1/image/?width=800'
    
    def get_download_url(self, obj):
        file_latest = obj.files.order_by('-timestamp').first()
        if file_latest:
            return f'/api/v4/documents/{obj.id}/files/{file_latest.id}/download/'
        return None

    class Meta:
        # Ensure no HTML rendering
        pass
```

**Checklist:**
- [ ] Verify `DAMDocumentDetailSerializer` returns JSON only
- [ ] Remove any HTML template rendering from API views
- [ ] Add `thumbnail_url`, `preview_url`, `download_url` fields
- [ ] Test with Postman/curl
- [ ] Update Swagger documentation

##### B1.2 TokenAuthentication Enable

```python
# mayan/settings/base.py — UPDATE

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # ADD THIS
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'ai_analysis': '10/minute',
    },
}

# Ensure rest_framework.authtoken is in INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'rest_framework.authtoken',
    ...
]
```

**Checklist:**
- [ ] Enable `TokenAuthentication`
- [ ] Add `rest_framework.authtoken` to `INSTALLED_APPS`
- [ ] Run migrations (`python manage.py migrate`)
- [ ] Test token obtain endpoint
- [ ] Test API access with token header

##### B1.3 CORS Configuration

```python
# mayan/settings/base.py — UPDATE

INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    ...
]

# Development CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite dev server
    'http://127.0.0.1:5173',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Production: Update to actual domain
# CORS_ALLOWED_ORIGINS = ['https://dam.yourdomain.com']
```

**Checklist:**
- [ ] Install `django-cors-headers` (already in requirements)
- [ ] Add `CorsMiddleware` to `MIDDLEWARE`
- [ ] Configure `CORS_ALLOWED_ORIGINS` for dev
- [ ] Test cross-origin requests from frontend
- [ ] Verify credentials (cookies) are passed

##### B1.4 Bulk Operations API

```python
# mayan/apps/documents/api_views/document_api_views.py — NEW ENDPOINT

class APIDocumentBulkOperationView(generics.GenericAPIView):
    """
    Bulk operations on multiple documents.
    
    POST /api/v4/documents/bulk/
    {
        "ids": [1, 2, 3],
        "action": "add_tags" | "remove_tags" | "move" | "delete",
        "data": { ... }
    }
    """
    serializer_class = BulkOperationSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ids = serializer.validated_data['ids']
        action = serializer.validated_data['action']
        data = serializer.validated_data.get('data', {})
        
        # Check permissions for each document
        documents = []
        for doc_id in ids:
            try:
                doc = Document.objects.get(pk=doc_id)
                AccessControlList.objects.check_access(
                    obj=doc,
                    permissions=(permission_document_edit,),
                    user=request.user
                )
                documents.append(doc)
            except (Document.DoesNotExist, PermissionDenied):
                continue
        
        # Execute action
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for doc in documents:
            try:
                if action == 'add_tags':
                    self._add_tags(doc, data.get('tag_ids', []))
                elif action == 'remove_tags':
                    self._remove_tags(doc, data.get('tag_ids', []))
                elif action == 'move':
                    self._move_to_cabinet(doc, data.get('cabinet_id'))
                elif action == 'delete':
                    self._trash_document(doc)
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'id': doc.id, 'error': str(e)})
        
        return Response(results)
    
    def _add_tags(self, document, tag_ids):
        for tag_id in tag_ids:
            tag = Tag.objects.get(pk=tag_id)
            document.tags.add(tag)
    
    def _remove_tags(self, document, tag_ids):
        for tag_id in tag_ids:
            document.tags.remove(tag_id)
    
    def _move_to_cabinet(self, document, cabinet_id):
        cabinet = Cabinet.objects.get(pk=cabinet_id)
        cabinet.document_add(document)
    
    def _trash_document(self, document):
        document.delete()  # Moves to trash


# Register in urls.py
urlpatterns = [
    path(
        'documents/bulk/',
        APIDocumentBulkOperationView.as_view(),
        name='document-bulk'
    ),
    ...
]
```

**Checklist:**
- [ ] Implement `APIDocumentBulkOperationView`
- [ ] Add `BulkOperationSerializer`
- [ ] Register URL pattern
- [ ] Test bulk add tags
- [ ] Test bulk delete
- [ ] Add Swagger documentation

---

#### Phase B2: Performance (Week 3-4)

**Goal:** Optimize API performance for Gallery view.

##### B2.1 N+1 Query Fix

```python
# mayan/apps/documents/api_views/document_api_views.py — UPDATE

class APIDocumentListView(generics.ListAPIView):
    """
    Optimized document list with related data prefetched.
    """
    
    def get_queryset(self):
        queryset = Document.valid.all()
        
        # Apply ACL filtering
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=queryset,
            user=self.request.user
        )
        
        # Optimize queries - prefetch related data
        queryset = queryset.select_related(
            'document_type'
        ).prefetch_related(
            Prefetch(
                'files',
                queryset=DocumentFile.objects.order_by('-timestamp')[:1],
                to_attr='file_latest_list'
            ),
            'tags',
            'ai_analysis'  # DAM extension
        )
        
        return queryset
    
    @property
    def file_latest(self):
        """Get cached file_latest from prefetch."""
        if hasattr(self, 'file_latest_list') and self.file_latest_list:
            return self.file_latest_list[0]
        return None
```

**Checklist:**
- [ ] Add `select_related` for ForeignKey fields
- [ ] Add `prefetch_related` for ManyToMany fields
- [ ] Test with Django Debug Toolbar
- [ ] Verify query count reduction
- [ ] Target: < 5 queries for list view

##### B2.2 Search Optimization

```python
# Verify Elasticsearch/Whoosh configuration
# mayan/apps/dynamic_search/backends/elasticsearch.py

# For large datasets, ensure Elasticsearch is used:
MAYAN_SEARCH_BACKEND = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticsearchSearchBackend'
MAYAN_SEARCH_BACKEND_ARGUMENTS = {
    'hosts': ['http://elasticsearch:9200']
}
```

**Checklist:**
- [ ] Verify search backend configuration
- [ ] Test search performance with 1000+ documents
- [ ] Add search result highlighting (optional)
- [ ] Configure search result limit

##### B2.3 Thumbnail Caching

```python
# Verify file_caching app is configured
# mayan/apps/file_caching/models.py

# Ensure cache is enabled for page images
CONVERTER_IMAGE_GENERATION_MAX_RETRIES = 3
```

**Checklist:**
- [ ] Verify thumbnail cache directory
- [ ] Configure cache TTL
- [ ] Test thumbnail generation
- [ ] Monitor cache hit ratio

---

#### Phase B3: S3 & Uploads (Week 5-6)

**Goal:** Ensure reliable file storage and upload handling.

##### B3.1 S3 Storage Verification

```python
# mayan/apps/documents/storages.py — VERIFY

# Ensure BegetS3Boto3Storage is properly configured
class BegetS3Boto3Storage(S3Boto3Storage):
    """
    Custom storage for Beget S3.
    """
    
    def _save(self, name, content):
        # Direct put_object for Beget compatibility
        ...
```

**Checklist:**
- [ ] Test S3 upload with real credentials
- [ ] Verify file retrieval works
- [ ] Test large file upload (>100MB)
- [ ] Verify presigned URLs work
- [ ] Test file deletion

##### B3.2 Chunked Upload Support

```python
# mayan/apps/sources/views.py — VERIFY chunked upload support

# Mayan uses sources for file intake
# Web upload source should handle large files
```

**Checklist:**
- [ ] Verify max upload size configuration
- [ ] Test file upload > 100MB
- [ ] Monitor memory usage during upload
- [ ] Add progress tracking (if not present)

##### B3.3 Document Type Configuration

**Checklist:**
- [ ] Create default Document Type for DAM assets
- [ ] Configure auto-tagging on upload
- [ ] Set up retention policies (optional)
- [ ] Configure OCR settings per type

---

#### Phase B4: Async & Webhooks (Week 7-8)

**Goal:** Enable real-time status updates for AI processing.

##### B4.1 AI Analysis Status Endpoint

```python
# mayan/apps/dam/api_views.py — NEW/VERIFY

class AIAnalysisStatusView(generics.GenericAPIView):
    """
    Get AI analysis status for a document.
    Used for polling from frontend.
    
    GET /api/dam/documents/{id}/analysis-status/
    """
    
    def get(self, request, document_id):
        document = get_object_or_404(Document, pk=document_id)
        
        # Check access
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_view,),
            user=request.user
        )
        
        try:
            analysis = document.ai_analysis
            return Response({
                'status': analysis.analysis_status,
                'provider': analysis.ai_provider,
                'completed_at': analysis.analysis_completed,
                'description': analysis.ai_description,
                'tags': analysis.ai_tags,
                'colors': analysis.dominant_colors
            })
        except DocumentAIAnalysis.DoesNotExist:
            return Response({
                'status': 'not_started',
                'message': 'AI analysis has not been initiated'
            })
```

**Checklist:**
- [ ] Implement status polling endpoint
- [ ] Test with running AI task
- [ ] Add ETag/Last-Modified headers for caching
- [ ] Document in Swagger

##### B4.2 WebSocket Setup (Optional)

```python
# For real-time updates, consider Django Channels
# This is optional - polling works for MVP

# mayan/apps/dam/consumers.py
class AIAnalysisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.group_name = f'ai_analysis_{self.document_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def analysis_status_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
```

**Checklist:**
- [ ] Evaluate WebSocket vs Polling
- [ ] If WebSocket: Install django-channels
- [ ] Configure Redis channel layer
- [ ] Test real-time updates

##### B4.3 Celery Task Integration

```python
# mayan/apps/dam/tasks.py — UPDATE

@shared_task(bind=True, max_retries=3)
def analyze_document_with_ai(self, document_id: int):
    """AI analysis task with status updates."""
    
    document = Document.objects.get(id=document_id)
    
    # Update status to 'processing'
    analysis, _ = DocumentAIAnalysis.objects.get_or_create(document=document)
    analysis.analysis_status = 'processing'
    analysis.save()
    
    # Send WebSocket notification (if configured)
    # channel_layer.group_send(...)
    
    try:
        result = perform_ai_analysis(document)
        
        # Update with results
        analysis.ai_description = result.get('description')
        analysis.ai_tags = result.get('tags')
        analysis.dominant_colors = result.get('colors')
        analysis.analysis_status = 'completed'
        analysis.analysis_completed = timezone.now()
        analysis.save()
        
        # Send completion notification
        # channel_layer.group_send(...)
        
    except Exception as exc:
        analysis.analysis_status = 'failed'
        analysis.save()
        raise self.retry(exc=exc)
```

**Checklist:**
- [ ] Update task to emit status changes
- [ ] Test task retry logic
- [ ] Monitor Celery queue
- [ ] Add task result logging

---

#### Phase B-Hotfix: Stability & Crash Recovery (Week 8-9)

**Goal:** Resolve critical backend crash blocking frontend integration.

**Status:** 🚨 **CRITICAL BLOCKER** — Frontend cannot complete auth flow due to 500 error on GET /api/v4/users/current/

**Impact:** Phase A-Fix cannot proceed until this is resolved. Stream A is completely blocked.

##### B-Hotfix.1: Patch UserSerializer S3 Access Errors

**Problem:** UserSerializer crashes when trying to access S3 for user avatars, causing 500 error.

**Solution:** Add try/except block to safely handle S3 connection failures.

```python
# mayan/apps/user_management/serializers.py — PATCH REQUIRED

class UserSerializer(serializers.ModelSerializer):
    """User serializer with safe S3 avatar handling."""

    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        """Safely get avatar URL with S3 error handling."""
        try:
            # Existing S3 avatar logic
            if hasattr(obj, 'avatar') and obj.avatar:
                return obj.avatar.url
            return None
        except Exception as e:
            # Log error but don't crash the API
            logger.warning(f"Failed to get avatar URL for user {obj.id}: {e}")
            return None  # Return None instead of crashing

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                 'is_active', 'date_joined', 'avatar_url']
```

**Checklist:**
- [ ] Locate `UserSerializer` in `mayan/apps/user_management/serializers.py`
- [ ] Add try/except block around avatar URL generation
- [ ] Add proper logging for S3 access failures
- [ ] Test GET `/api/v4/users/current/` returns 200 OK
- [ ] Verify no 500 errors when S3 is unreachable

##### B-Hotfix.2: Validate S3 Connection on Startup

**Problem:** Backend starts successfully even when S3 is misconfigured, causing runtime crashes.

**Solution:** Add S3 connectivity check in app ready() method.

```python
# mayan/apps/user_management/apps.py — ADD CHECK

from django.apps import AppConfig
from django.core.checks import Error, register

class UserManagementAppConfig(AppConfig):
    name = 'mayan.apps.user_management'
    verbose_name = _('User management')

    def ready(self):
        """Validate S3 connection on startup."""
        super().ready()

        # Check S3 connectivity
        self._check_s3_connectivity()

    def _check_s3_connectivity(self):
        """Validate S3 storage backend is accessible."""
        try:
            from django.core.files.storage import default_storage

            # Try to access S3 (simple HEAD request to bucket)
            if hasattr(default_storage, 'bucket'):
                # This will fail if S3 credentials are wrong
                default_storage.bucket.head()

            logger.info("S3 connectivity check passed")
        except Exception as e:
            logger.error(f"S3 connectivity check failed: {e}")
            # Don't crash startup, just log warning
            # Consider: raise Error(f'S3 connection failed: {e}') for strict mode
```

**Checklist:**
- [ ] Add S3 connectivity check to `apps.py`
- [ ] Test with valid S3 credentials (should pass)
- [ ] Test with invalid S3 credentials (should warn but not crash)
- [ ] Verify check runs on `python manage.py check`
- [ ] Add to CI/CD pipeline for deployment validation

##### B-Hotfix.3: Verify User API Endpoint

**Problem:** GET /api/v4/users/current/ returns 500 instead of user data.

**Solution:** Comprehensive testing and validation.

```bash
# Test commands for verification

# 1. Test with authenticated user
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8080/api/v4/user_management/users/current/

# Should return:
# {
#   "id": 1,
#   "username": "admin",
#   "email": "admin@localhost",
#   "first_name": "",
#   "last_name": "",
#   "is_active": true,
#   "date_joined": "2025-12-03T...",
#   "avatar_url": null
# }

# 2. Test error handling when S3 is down
# (Simulate S3 outage and verify 200 response with avatar_url: null)

# 3. Test with unauthenticated request
curl http://localhost:8080/api/v4/user_management/users/current/
# Should return 401 Unauthorized (not 500)
```

**Checklist:**
- [ ] Test GET `/api/v4/users/current/` with valid token → 200 OK
- [ ] Test with invalid token → 401 Unauthorized
- [ ] Test with S3 outage → 200 OK (avatar_url: null)
- [ ] Test with no avatar set → 200 OK (avatar_url: null)
- [ ] Verify no 500 errors in any scenario
- [ ] Add to automated API tests

---

#### Phase A-Fix: Integration Polish & Correction (Week 9-10) 🚫 **DEPENDENT ON B-HOTFIX**

**Status:** ⏸️ **BLOCKED** — Cannot proceed until GET /api/v4/users/current/ is stable.

**Dependency:** Phase A-Fix requires working authentication flow. Frontend login depends on this endpoint.

**Next Steps:** Complete B-Hotfix first, then resume A-Fix.

---

#### Phase B-Fix: Backend Stubs & Tuning (Week 9-10)

**Goal:** Provide missing backend endpoints and optimize performance for 100% integration.

##### B-Fix.1: Missing Endpoints Implementation

**Special Collections API:**

```python
# mayan/apps/documents/api_views/document_api_views.py — NEW

class APIDocumentFavoritesView(generics.ListAPIView):
    """
    Get user's favorite documents.
    Requires a favorites relationship (Tag or custom model).
    """
    serializer_class = APIDocumentListSerializer

    def get_queryset(self):
        # Implementation depends on how favorites are stored
        # Option 1: Special tag
        favorite_tag = Tag.objects.get(label='favorite')
        return favorite_tag.documents.all()

        # Option 2: Custom Favorite model
        # return self.request.user.favorite_documents.all()

class APIDocumentRecentView(generics.ListAPIView):
    """
    Get recently accessed documents for current user.
    """
    serializer_class = APIDocumentListSerializer

    def get_queryset(self):
        # Implementation depends on access logging
        return Document.objects.filter(
            documentaccesslog__user=self.request.user
        ).order_by('-documentaccesslog__timestamp').distinct()[:50]

class APIDocumentMyUploadsView(generics.ListAPIView):
    """
    Get documents uploaded by current user.
    """
    serializer_class = APIDocumentListSerializer

    def get_queryset(self):
        return Document.objects.filter(
            files__user=self.request.user
        ).distinct()
```

**Checklist:**
- [ ] Implement `/api/v4/documents/favorites/` endpoint
- [ ] Implement `/api/v4/documents/recent/` endpoint
- [ ] Implement `/api/v4/documents/my-uploads/` endpoint
- [ ] Implement `/api/v4/documents/shared/` endpoint
- [ ] Add proper permissions and ACL checks

**Activity Feed API:**

```python
# mayan/apps/events/api_views.py — NEW

class APIEventActivityView(generics.ListAPIView):
    """
    Get activity feed for dashboard.
    Shows recent document operations, user actions, etc.
    """
    serializer_class = EventSerializer

    def get_queryset(self):
        # Get recent events from Event model
        return Event.objects.filter(
            # Filter relevant event types
            event_type__in=['document_created', 'document_edited', 'document_downloaded']
        ).order_by('-timestamp')[:50]
```

**Checklist:**
- [ ] Implement `/api/v4/events/activity/` endpoint
- [ ] Define relevant event types for activity feed
- [ ] Add pagination support
- [ ] Ensure proper event logging is enabled

**Storage Metrics API:**

```python
# mayan/apps/dam/api_views.py — NEW

class APIStorageMetricsView(generics.RetrieveAPIView):
    """
    Get storage usage metrics for dashboard.
    """

    def get(self, request):
        # Calculate storage metrics
        total_size = DocumentFile.objects.aggregate(
            total=Sum('size')
        )['total'] or 0

        by_type = DocumentFile.objects.values('mimetype').annotate(
            count=Count('id'),
            size=Sum('size')
        )

        return Response({
            'total_size': total_size,
            'used_size': total_size,  # For now, assume all used
            'available_size': 100 * 1024 * 1024 * 1024,  # 100GB placeholder
            'usage_percentage': (total_size / (100 * 1024 * 1024 * 1024)) * 100,
            'by_type': list(by_type)
        })
```

**Checklist:**
- [ ] Implement `/api/dam/storage-metrics/` endpoint
- [ ] Add proper caching for performance
- [ ] Handle large file counts efficiently

##### B-Fix.2: Performance Tuning

**Query Optimization Verification:**

```python
# Verify all list endpoints use select_related/prefetch_related
# Check Django Debug Toolbar output
# Target: < 5 queries per list request

# Example optimization check:
def test_document_list_performance():
    # Simulate document list request
    queryset = Document.objects.select_related('document_type').prefetch_related(
        Prefetch('files', queryset=DocumentFile.objects.order_by('-timestamp')[:1]),
        'tags', 'ai_analysis'
    )
    # Assert: queryset.query.count == expected low number
```

**Checklist:**
- [ ] Run performance tests with Django Debug Toolbar
- [ ] Verify N+1 query elimination
- [ ] Add database indexes if needed
- [ ] Optimize thumbnail generation
- [ ] Implement caching for frequently accessed data

##### B-Fix.3: Error Handling & Monitoring

**API Error Standardization:**

```python
# mayan/settings/base.py — UPDATE

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'mayan.apps.rest_api.handlers.custom_exception_handler',
    # ... other settings
}

# mayan/apps/rest_api/handlers.py — ENSURE
def custom_exception_handler(exc, context):
    """
    Standardized error responses with error_code field.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Add error_code for frontend handling
        if isinstance(exc, ValidationError):
            response.data['error_code'] = 'VALIDATION_ERROR'
        elif isinstance(exc, PermissionDenied):
            response.data['error_code'] = 'PERMISSION_DENIED'
        # ... other error types

    return response
```

**Checklist:**
- [ ] Standardize error response format
- [ ] Add error codes for frontend handling
- [ ] Implement proper logging
- [ ] Set up error monitoring (Sentry)
- [ ] Add health check endpoints

---

## 3. Integration Points

### 3.1 Checkpoint Schedule

| Checkpoint | Week | Participants | Goal | Deliverables |
|------------|------|--------------|------|--------------|
| **#1** | 2 | Both | Auth Handshake | Login works with real backend |
| **#2** | 4 | Both | Gallery Works | Real documents displayed in Gallery |
| **#3** | 6 | Both | Full CRUD | Upload, Edit, Delete all functional |
| **#4** | 8 | Both | Admin Panel | All admin features work |
| **#4.5** | 9 | Backend (Дмитрий) | Auth Stability | GET /api/v4/users/current/ returns 200 OK |
| **#5** | 11 | Both | 100% Integration | No mock data, all features real |

### 3.2 Contract Interface (OpenAPI)

**Location:** `/api/schema/swagger-ui/` (auto-generated by drf-yasg)

**Critical Endpoints Contract:**

```yaml
# Core Document Endpoints (v4)
/api/v4/documents/:
  GET:
    responses:
      200:
        schema:
          type: object
          properties:
            count: integer
            next: string|null
            previous: string|null
            results:
              type: array
              items:
                $ref: '#/definitions/Document'

/api/v4/documents/{id}/:
  GET:
    responses:
      200:
        schema:
          $ref: '#/definitions/DocumentDetail'

# DAM Extension Endpoints
/api/dam/document-detail/{id}/:
  GET:
    responses:
      200:
        schema:
          $ref: '#/definitions/DAMDocumentDetail'

/api/dam/ai-analysis/analyze/:
  POST:
    requestBody:
      schema:
        type: object
        properties:
          document_id: integer
          ai_service: string
    responses:
      202:
        schema:
          type: object
          properties:
            task_id: string
            status: string
```

**Checklist:**
- [ ] Generate OpenAPI schema
- [ ] Share schema with frontend developer
- [ ] Update schema after API changes
- [ ] Use schema for TypeScript type generation (optional)

### 3.3 Communication Protocol

| Item | Method |
|------|--------|
| **Daily Sync** | Slack/Telegram channel `#dam-integration` |
| **Weekly Review** | Video call (Mondays, 30 min) |
| **API Changes** | PR review + Swagger update |
| **Blockers** | Immediate escalation via chat |

---

## 4. Git Strategy

### 4.1 Branch Structure

```
main (production)
│
├── develop (integration)
│   │
│   ├── feature/frontend-api-integration (Виталий)
│   │   ├── feature/frontend-auth-refactor
│   │   ├── feature/frontend-asset-adapter
│   │   ├── feature/frontend-upload-service
│   │   └── feature/frontend-admin-api
│   │
│   └── feature/backend-api-v2 (Дмитрий)
│       ├── feature/backend-token-auth
│       ├── feature/backend-bulk-operations
│       ├── feature/backend-s3-optimization
│       └── feature/backend-ai-status
│
└── hotfix/* (production fixes)
```

### 4.2 Workflow

```
1. Create feature branch from develop
   git checkout develop
   git pull origin develop
   git checkout -b feature/frontend-auth-refactor

2. Work on feature (commits)
   git commit -m "feat(auth): implement token-based authentication"

3. Push and create PR
   git push origin feature/frontend-auth-refactor
   # Create PR to develop

4. Code review
   - At least 1 approval required
   - CI must pass

5. Merge to develop
   # Squash merge preferred

6. Weekly merge to main (after checkpoint)
   # After successful checkpoint testing
```

### 4.3 Commit Convention

```
<type>(<scope>): <description>

Types:
- feat: New feature
- fix: Bug fix
- refactor: Code refactoring
- docs: Documentation
- test: Tests
- chore: Build/config changes

Scopes:
- auth: Authentication
- gallery: Gallery view
- upload: Upload functionality
- admin: Admin panel
- api: API changes
- store: Pinia stores
```

### 4.4 PR Template

```markdown
## Description
Brief description of changes

## Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Refactor
- [ ] Documentation

## Checklist
- [ ] Tests pass
- [ ] Linting passes
- [ ] API contract unchanged (or documented)
- [ ] Swagger updated (backend)
- [ ] TypeScript types updated (frontend)

## Screenshots (if UI change)

## Related Issues
Closes #123
```

---

## 5. Risk Management

### 5.1 Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Auth API crashes (500 errors)** | High | Critical | **B-Hotfix Phase** - Patch UserSerializer S3 handling |
| **API contract mismatch** | Medium | High | Weekly sync, shared Swagger |
| **S3 upload issues** | Medium | High | Early testing, fallback to local |
| **Performance degradation** | Low | Medium | Load testing at checkpoints |
| **Auth token conflicts** | Low | Medium | Clear session strategy |
| **AI service unavailable** | Medium | Low | Graceful degradation |
| **useMock persistence bug** | High | High | Remove from persist paths immediately |
| **Upload system broken** | High | Critical | Fix uploadWorkflowStore in A-Fix phase |
| **Missing backend endpoints** | Medium | High | Implement stubs in B-Fix phase |

### 5.2 Contingency Plans

| Issue | Contingency |
|-------|-------------|
| Backend API delay | Frontend continues with enhanced mocks |
| Frontend delay | Backend provides curl examples for testing |
| S3 failure | Fallback to local storage |
| AI service down | Skip AI analysis, manual tagging |

---

## 6. Timeline & Milestones

### 6.1 Gantt Chart (Text)

```
Week 1  │████████████████│ A1: Foundation      │ B1: API Gap Fill
Week 2  │████████████████│                     │
        │       ▼        │ CHECKPOINT #1: Auth │
Week 3  │████████████████│ A2: Read-Only      │ B2: Performance
Week 4  │████████████████│                     │
        │       ▼        │ CHECKPOINT #2: Gallery │
Week 5  │████████████████│ A3: Write Layer    │ B3: S3 & Uploads
Week 6  │████████████████│                     │
        │       ▼        │ CHECKPOINT #3: CRUD │
Week 7  │████████████████│ A4: Admin UI       │ B4: Async
Week 8  │████████████████│                     │
        │       ▼        │ CHECKPOINT #4: Admin │
Week 8  │████████████████│ B-Hotfix: Stability│ A-Fix: BLOCKED
Week 9  │████████████████│ & Crash Recovery   │ (Waiting for B-Hotfix)
        │       ▼        │ CHECKPOINT #4.5: Auth│ Stable
Week 10 │████████████████│ A-Fix: Integration │ B-Fix: Backend
Week 11 │████████████████│ Polish & Correction│ Stubs & Tuning
        │       ▼        │ CHECKPOINT #5: 100% │
Week 12 │████████████████│ Testing & Polish   │ Integration
Week 13 │████████████████│ Production Deploy  │
```

### 6.2 Milestones

| Milestone | Date | Criteria |
|-----------|------|----------|
| **M1: Auth Complete** | Week 2 | Login/logout works with real backend |
| **M2: Gallery Live** | Week 4 | Gallery shows real documents |
| **M3: Full CRUD** | Week 6 | Upload, edit, delete functional |
| **M4: Admin Ready** | Week 8 | Admin panel fully functional |
| **M4.5: Auth Stable** | Week 9 | GET /api/v4/users/current/ returns 200 OK |
| **M5: 100% Integration** | Week 11 | No mock data, all features work |
| **M6: Production** | Week 13 | Deployed to production |

---

## 7. Definition of Done

### 7.1 Feature DoD

A feature is considered "Done" when:

- [ ] Code is written and passes linting
- [ ] Unit tests pass (>80% coverage for new code)
- [ ] Integration test passes (if applicable)
- [ ] API contract is documented/updated
- [ ] PR is reviewed and approved
- [ ] Merged to develop branch
- [ ] Tested in staging environment
- [ ] No regressions in existing functionality

### 7.2 Checkpoint DoD

A checkpoint is considered "Complete" when:

- [ ] All assigned features for the phase are Done
- [ ] End-to-end flow works (frontend → backend)
- [ ] Performance is acceptable (<2s page load)
- [ ] No critical bugs
- [ ] Both developers have signed off

### 7.2.5 B-Hotfix Checkpoint DoD

**Checkpoint #4.5 (Auth Stability)** is considered "Complete" when:

- [ ] GET `/api/v4/users/current/` returns 200 OK for authenticated users
- [ ] No 500 Internal Server Errors when S3 is unreachable
- [ ] UserSerializer handles S3 avatar access gracefully
- [ ] S3 connectivity check passes on application startup
- [ ] Frontend login flow completes successfully
- [ ] Backend developer (Дмитрий) has signed off

### 7.3 Production DoD

Production deployment criteria:

- [ ] All checkpoints complete
- [ ] Security audit passed (no exposed secrets)
- [ ] Load testing passed (100 concurrent users)
- [ ] Backup/restore tested
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Stakeholder sign-off

---

## 📎 Appendix

### A. Environment Setup

#### Frontend (.env.development)
```bash
VITE_API_URL=http://localhost:8080
VITE_USE_REAL_API=true
VITE_ENABLE_AI=true
```

#### Backend (.env)
```bash
MAYAN_DATABASES='{"default":{"ENGINE":"django.db.backends.postgresql","NAME":"mayan","USER":"mayan","PASSWORD":"xxx","HOST":"postgresql","PORT":"5432"}}'
MAYAN_CELERY_BROKER_URL=amqp://mayan:xxx@rabbitmq:5672/mayan
MAYAN_LOCK_MANAGER_BACKEND=mayan.apps.lock_manager.backends.redis_lock.RedisLock
```

### B. Quick Reference: Endpoint Mapping

| Frontend Service | Correct Backend Endpoint |
|------------------|--------------------------|
| `authService.login()` | `POST /api/v4/auth/token/obtain/` |
| `authService.getCurrentUser()` | `GET /api/v4/user_management/users/current/` |
| `assetService.getAssets()` | `GET /api/v4/documents/` |
| `assetService.getAsset(id)` | `GET /api/dam/document-detail/{id}/` |
| `uploadService.upload()` | `POST /api/v4/documents/` + `POST .../files/` |
| `tagService.getTags()` | `GET /api/v4/tags/` |
| `collectionsService.getCollections()` | `GET /api/v4/cabinets/` |

### C. Testing Checklist

#### Auth Flow
- [ ] Login with valid credentials → Token received
- [ ] Login with invalid credentials → Error message
- [ ] Access protected route without token → Redirect to login
- [ ] Logout → Token cleared, redirected to login

#### Gallery
- [ ] Load first page of documents
- [ ] Scroll to load more (pagination)
- [ ] Search returns filtered results
- [ ] Thumbnails display correctly
- [ ] Click to view details

#### Upload
- [ ] Upload small file (<5MB)
- [ ] Upload large file (>50MB) with chunked upload
- [ ] Upload multiple files with progress tracking
- [ ] Real progress bars (not mock setTimeout)
- [ ] Error handling for failed upload
- [ ] Resume interrupted uploads (if implemented)

#### Download
- [ ] Download single asset
- [ ] Download multiple assets
- [ ] Download from S3 presigned URLs
- [ ] Error handling for expired URLs

#### Special Collections
- [ ] Favorites collection shows real data
- [ ] Recent documents loads correctly
- [ ] My Uploads filters by user
- [ ] Shared documents displays properly

#### Dashboard & Analytics
- [ ] Activity feed loads real events
- [ ] Storage metrics display correctly
- [ ] Dashboard loads without mock data

---

**Document Version:** 1.3 (Added B-Hotfix Phase - Critical Auth Blocker)
**Created:** 03 December 2025
**Last Updated:** 03 December 2025
**Authors:** Technical Project Manager & Solutions Architect

