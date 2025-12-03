/**
 * Service Adapters - Transform external API responses to Frontend format
 */

// Document Adapter (Mayan EDMS → Frontend) - Legacy
export {
  // Main adapter functions
  adaptDocument,
  adaptDocuments,
  adaptPaginatedResponse,
  adaptAIAnalysis,
  
  // Reverse adapters (Frontend → Mayan)
  toMayanDocumentUpdate,
  toMayanTagAttach,
  toMayanMetadataUpdate,
  
  // Configuration
  setAdapterConfig,
  getAdapterConfig,
  
  // Utility functions
  getThumbnailUrl,
  getPreviewUrl,
  getAssetType,
  toFullUrl,
} from './documentAdapter'

// Type exports from documentAdapter
export type {
  MayanDocument,
  MayanDocumentFile,
  MayanDocumentVersion,
  MayanAIAnalysis,
  MayanMetadataValue,
  MayanTag,
  MayanCabinet,
  MayanPaginatedResponse,
  DocumentAdapterConfig,
} from './documentAdapter'

// ============================================================================
// Mayan Adapter (Optimized API) - Phase A2
// ============================================================================

export {
  // Main adapter functions
  adaptBackendAsset,
  adaptBackendAssets,
  adaptBackendPaginatedResponse,
  adaptBackendAIAnalysis,
  adaptBackendTags,
  adaptBackendMetadata,
  
  // Configuration
  setBaseUrl,
} from './mayanAdapter'

// Type exports from mayanAdapter
export type {
  BackendOptimizedDocument,
  BackendDocumentFile,
  BackendDocumentType,
  BackendAIAnalysis,
  BackendTag,
  BackendMetadata,
  BackendPaginatedResponse,
} from './mayanAdapter'

