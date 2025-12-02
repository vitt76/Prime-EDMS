/**
 * Service Adapters - Transform external API responses to Frontend format
 */

// Document Adapter (Mayan EDMS → Frontend)
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

// Type exports
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

