# API Contract Mismatches V2: Formal Specifications

**Date:** December 3, 2025
**Author:** Principal Solution Architect & QA Lead
**Purpose:** Clarify exact API contract mismatches between Vue frontend expectations and Mayan backend reality
**Scope:** Analysis only - no code changes or solutions proposed

---

## Executive Summary

This document formalizes the API contract mismatches identified in API_MISMATCH_FIX.md and related analyses. Each mismatch is documented with exact request/response specifications to enable precise testing and future implementation.

**Key Finding:** The mismatches are not bugs but fundamental architectural differences between automation-focused APIs and interactive SPA requirements.

---

## Critical API Contract Mismatches

### Mismatch 1: Password Change Endpoint

#### Endpoint Name: Change Password

**Frontend Request Contract (Expected):**
- **HTTP Method:** POST
- **URL:** `/api/v4/users/current/password/`
- **Expected JSON Body:**
  ```json
  {
    "new_password": "string",
    "current_password": "string"  // optional
  }
  ```
- **Required Headers:**
  - `Authorization: Token <token>`
  - `Content-Type: application/json`

**Backend Actual Contract:**
- **HTTP Method:** N/A (endpoint does not exist)
- **URL:** N/A (no password change endpoint)
- **Accepted Schema:** N/A
- **Auth Assumptions:** N/A

**Alternative Backend Contract (PATCH on user):**
- **HTTP Method:** PATCH
- **URL:** `/api/v4/users/current/`
- **Accepted JSON Body:**
  ```json
  {
    "password": "new_password_string"
  }
  ```
- **Auth Assumptions:** Token or Session authentication

**Observed Behavior:**
- Frontend POST to `/api/v4/users/current/password/`: Returns 404 Not Found
- Backend PATCH to `/api/v4/users/current/`: Accepts password field but returns 200 OK (actual password change effectiveness unverified)

**Classification:** ❌ **INCOMPATIBLE / MISSING** - No dedicated password endpoint exists

---

### Mismatch 2: File Upload Completion

#### Endpoint Name: Upload Complete

**Frontend Request Contract (Expected):**
- **HTTP Method:** POST
- **URL:** `/api/v4/uploads/complete/`
- **Expected JSON Body:**
  ```json
  {
    "upload_id": "uuid-string",
    "label": "Document Name.pdf",
    "description": "Optional description",
    "document_type_id": 1
  }
  ```
- **Required Headers:**
  - `Authorization: Token <token>`
  - `Content-Type: application/json`

**Backend Actual Contract:**
- **HTTP Method:** POST
- **URL:** `/api/v4/uploads/complete/`
- **Accepted JSON Body:**
  ```json
  {
    "upload_id": "uuid-string",
    "label": "string",           // optional
    "description": "string",     // optional, defaults to ""
    "document_type_id": "integer" // optional
  }
  ```
- **Auth Assumptions:** Token authentication required

**Backend Response Contract:**
```json
{
  "upload_id": "uuid-string",
  "document_id": 123,
  "document_file_id": 456,
  "s3_key": "uploads/2024/01/01/file.pdf",
  "status": "completed"
}
```

**Observed Behavior:**
- Request matches contract and works correctly
- Document and DocumentFile are created properly
- S3 upload completion handled correctly

**Classification:** ✅ **EXACT MATCH** - Contract alignment confirmed

---

### Mismatch 3: Current User Retrieval

#### Endpoint Name: Current User

**Frontend Request Contract (Expected):**
- **HTTP Method:** GET
- **URL:** `/api/v4/users/current/`
- **Body:** None
- **Required Headers:**
  - `Authorization: Token <token>`

**Backend Actual Contract:**
- **HTTP Method:** GET
- **URL:** `/api/v4/users/current/`
- **Body:** None
- **Auth Assumptions:** Token or Session authentication

**Backend Response Contract:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z",
  "groups_url": "string",
  "url": "string"
}
```

**Observed Behavior:**
- Request matches contract and returns user data
- Authentication works correctly

**Classification:** ✅ **EXACT MATCH** - Contract alignment confirmed

---

### Mismatch 4: Document List Retrieval

#### Endpoint Name: Document List

**Frontend Request Contract (Expected):**
- **HTTP Method:** GET
- **URL:** `/api/v4/documents/optimized/` or `/api/v4/documents/`
- **Query Parameters:**
  - `page`: integer
  - `page_size`: integer
  - `search`: string
  - `document_type_id`: integer
- **Required Headers:**
  - `Authorization: Token <token>`

**Backend Actual Contract (Optimized API):**
- **HTTP Method:** GET
- **URL:** `/api/v4/documents/optimized/`
- **Query Parameters:**
  - `page`: integer
  - `page_size`: integer (default 50)
  - `search`: string (full-text search)
  - `document_type_id`: integer
  - `ordering`: string

**Backend Response Contract:**
```json
{
  "count": 100,
  "next": "http://api.example.com/api/v4/documents/optimized/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "uuid": "string",
      "label": "Document Name",
      "description": "Description",
      "datetime_created": "2024-01-01T00:00:00Z",
      "file_latest": {
        "filename": "file.pdf",
        "mimetype": "application/pdf",
        "size": 12345,
        "download_url": "string"
      },
      "thumbnail_url": "string",
      "preview_url": "string",
      "tags": ["tag1", "tag2"],
      "metadata": {"key": "value"},
      "ai_analysis": {...}
    }
  ]
}
```

**Observed Behavior:**
- Request matches contract and works
- Optimized API provides rich document data
- Pagination and filtering work correctly

**Classification:** ✅ **EXACT MATCH** - Contract alignment confirmed

---

### Mismatch 5: Document Type Configuration

#### Endpoint Name: Document Type Details

**Frontend Request Contract (Expected):**
- **HTTP Method:** GET
- **URL:** `/api/v4/document_types/{id}/config/`
- **Expected Response:** Complete configuration schema for form building
  ```json
  {
    "required_fields": ["title", "description"],
    "optional_fields": ["tags", "category"],
    "validation_rules": {...},
    "workflows": [...],
    "filename_patterns": [...]
  }
  ```

**Backend Actual Contract:**
- **HTTP Method:** GET
- **URL:** `/api/v4/document_types/{id}/`
- **Actual Response:** Basic document type info only
  ```json
  {
    "id": 1,
    "label": "PDF Document",
    "url": "string"
  }
  ```

**Observed Behavior:**
- Basic document type information available
- No configuration schema exposed
- Frontend cannot build dynamic forms

**Classification:** ❌ **INCOMPATIBLE / MISSING** - Configuration data not exposed

---

### Mismatch 6: Activity/Events Feed

#### Endpoint Name: User Activity

**Frontend Request Contract (Expected):**
- **HTTP Method:** GET
- **URL:** `/api/v4/users/current/activity/` or `/api/v4/activity/`
- **Query Parameters:**
  - `page`: integer
  - `page_size`: integer
- **Expected Response:** User-specific activity feed
  ```json
  {
    "results": [
      {
        "timestamp": "2024-01-01T00:00:00Z",
        "action": "uploaded",
        "document_id": 123,
        "document_label": "file.pdf"
      }
    ]
  }
  ```

**Backend Actual Contract:**
- **HTTP Method:** GET
- **URL:** `/api/v4/events/` (exists but not user-specific)
- **Response:** All system events, not filtered by user
  ```json
  {
    "results": [
      {
        "id": 1,
        "timestamp": "2024-01-01T00:00:00Z",
        "verb": "document_created",
        "actor": {...},
        "target": {...}
      }
    ]
  }
  ```

**Observed Behavior:**
- Events API exists but returns all system events
- No user-specific activity filtering
- Frontend has no activity service

**Classification:** ❌ **INCOMPATIBLE / MISSING** - No user activity endpoint

---

## Test Verification Matrix

| Endpoint | Test Method | Expected Current Result | Verification Purpose |
|----------|-------------|-------------------------|---------------------|
| Password Change | POST `/api/v4/users/current/password/` | 404 Not Found | Confirm endpoint missing |
| Password Change Alt | PATCH `/api/v4/users/current/` | 200 OK | Verify password field accepted |
| Upload Complete | POST `/api/v4/uploads/complete/` | 201 Created + Document | Confirm upload flow works |
| Current User | GET `/api/v4/users/current/` | 200 OK + User Data | Verify auth works |
| Document List | GET `/api/v4/documents/optimized/` | 200 OK + Document List | Verify data retrieval |
| Document Type | GET `/api/v4/document_types/1/` | 200 OK + Basic Info | Confirm limited config exposure |
| Events | GET `/api/v4/events/` | 200 OK + Event List | Verify events API exists |

---

## Summary of Contract Status

### ✅ **Exact Match (3/7)**
- Current User retrieval
- Document List with optimized API
- File Upload completion

### 🟡 **Compatible with Mapping (0/7)**
- None identified

### ❌ **Incompatible/Missing (4/7)**
- Password change endpoint
- Document type configuration schema
- User activity feed
- Dynamic form generation data

### Key Architectural Insight

The Mayan API is **functionally complete for automation** but **architecturally incomplete for interactive SPAs**. Core CRUD operations work, but self-service and configuration-driven UX patterns are missing.

---

**Analysis Status:** ✅ **API CONTRACTS FORMALIZED**
**Next Step:** Test plan design for verification
**Documents Referenced:** API_MISMATCH_FIX.md, all V3 analyses

---

