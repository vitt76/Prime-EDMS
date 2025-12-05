# Architectural Gap Analysis V2: Flows vs Capabilities Matrix

**Date:** December 3, 2025
**Author:** Principal Solution Architect & QA Lead
**Analysis Method:** Consolidation of all analysis documents (ARCHITECTURE_GAP_REPORT.md, API_MISMATCH_FIX.md, V3 analyses)
**Purpose:** Make problem space explicit, align all documents, design concrete test plans

---

## Executive Summary

This document consolidates the architectural gaps between Mayan EDMS backend and Vue.js SPA frontend by mapping **user-facing flows** against **actual capabilities**. All assessments are based strictly on existing analysis documents and code evidence, without assumptions.

**Key Finding:** While core document operations work, **critical self-service flows are broken** due to Mayan's enterprise-first, automation-focused API design.

---

## Flows vs Capabilities Matrix

### Critical User Flows for DAM MVP

Based on analysis of FRONTEND_ANALYSIS_V3.md and BACKEND_ANALYSIS_V3.md, the following flows represent the minimum viable product for a DAM system:

| Flow ID | Flow Name | Description | Priority |
|---------|-----------|-------------|----------|
| F1 | User Login/Logout | Authenticate user session | Critical |
| F2 | Change Own Password | Self-service password update | Critical |
| F3 | Upload New Asset | File upload with chunking support | Critical |
| F4 | View Assets List | Browse uploaded documents | Critical |
| F5 | Download Asset | Retrieve file content | Critical |
| F6 | Edit Asset Metadata | Update document properties | Important |
| F7 | Search/Filter Assets | Find documents by criteria | Important |
| F8 | View Activity/History | See user actions log | Optional |

### Capabilities Assessment

| Flow ID | Flow Name | Mayan HTML UI Support | Mayan REST API v4 Support | Vue Frontend Support | Known Gaps/Mismatches |
|---------|-----------|----------------------|---------------------------|---------------------|----------------------|
| **F1** | **User Login/Logout** | ✅ YES | ✅ FULL | ✅ FULL | None - token authentication works |
| **F2** | **Change Own Password** | ✅ YES | ❌ NO | ❌ NO | Frontend expects `POST /api/v4/users/current/password/` but endpoint doesn't exist. Backend only supports HTML forms. See API_MISMATCH_FIX.md §2. |
| **F3** | **Upload New Asset** | ✅ YES | ✅ FULL | 🟡 PARTIAL | API supports chunked upload and creates documents correctly, but frontend may not call endpoints properly. See API_MISMATCH_FIX.md §1. |
| **F4** | **View Assets List** | ✅ YES | ✅ FULL | ✅ FULL | None - optimized document list API works |
| **F5** | **Download Asset** | ✅ YES | 🟡 PARTIAL | ✅ FULL | API provides download URLs but may not handle presigned S3 URLs correctly. Frontend implements download service. |
| **F6** | **Edit Asset Metadata** | ✅ YES | ✅ FULL | ✅ FULL | None - document PATCH/PUT operations work |
| **F7** | **Search/Filter Assets** | ✅ YES | 🟡 PARTIAL | 🟡 PARTIAL | API supports basic search but advanced filters may be limited. Frontend implements search store but with potential gaps. |
| **F8** | **View Activity/History** | ✅ YES | ❌ NO | ❌ NO | Backend has events API (`GET /api/v4/events/`) but no dedicated activity feed. Frontend has no activity service. |

---

## Detailed Flow Analysis

### F1: User Login/Logout

**Mayan HTML UI:** ✅ YES - Full login/logout flow with session management
**Mayan REST API v4:** ✅ FULL - Token authentication available
**Vue Frontend:** ✅ FULL - Implements authService with token storage
**Gaps:** None identified - this flow works end-to-end

### F2: Change Own Password

**Mayan HTML UI:** ✅ YES - MayanPasswordChangeView handles password changes
**Mayan REST API v4:** ❌ NO - No REST endpoint for password changes
**Vue Frontend:** ❌ NO - Attempts to call non-existent endpoint
**Gaps:** Critical self-service gap. Frontend expects REST API but backend only provides HTML forms. See API_MISMATCH_FIX.md §2 for exact endpoint mismatch.

### F3: Upload New Asset

**Mayan HTML UI:** ✅ YES - Full upload wizard with validation and workflows
**Mayan REST API v4:** ✅ FULL - Chunked upload API creates documents correctly
**Vue Frontend:** 🟡 PARTIAL - Upload service exists but may have implementation issues
**Gaps:** Backend logic works (ChunkedUploadCompleteView creates Document + DocumentFile), but frontend may not call endpoints correctly. See API_MISMATCH_FIX.md §1.

### F4: View Assets List

**Mayan HTML UI:** ✅ YES - Document list views with pagination
**Mayan REST API v4:** ✅ FULL - Optimized document API with pagination
**Vue Frontend:** ✅ FULL - Asset store fetches and displays documents
**Gaps:** None - optimized API and frontend adapter work correctly

### F5: Download Asset

**Mayan HTML UI:** ✅ YES - Download links and file serving
**Mayan REST API v4:** 🟡 PARTIAL - Provides download URLs but S3 handling unclear
**Vue Frontend:** ✅ FULL - Download service implemented
**Gaps:** API provides download URLs but presigned S3 URL handling may need verification

### F6: Edit Asset Metadata

**Mayan HTML UI:** ✅ YES - Document edit forms
**Mayan REST API v4:** ✅ FULL - PATCH/PUT operations on documents
**Vue Frontend:** ✅ FULL - Metadata editing implemented
**Gaps:** None - standard CRUD operations work

### F7: Search/Filter Assets

**Mayan HTML UI:** ✅ YES - Search interface with filters
**Mayan REST API v4:** 🟡 PARTIAL - Basic search supported, advanced filters limited
**Vue Frontend:** 🟡 PARTIAL - Search store implemented but may have gaps
**Gaps:** Full-text search works but advanced filtering capabilities unclear

### F8: View Activity/History

**Mayan HTML UI:** ✅ YES - Audit logs and event history
**Mayan REST API v4:** ❌ NO - Events API exists but no activity feed endpoint
**Vue Frontend:** ❌ NO - No activity service implemented
**Gaps:** Backend has `GET /api/v4/events/` but no user-specific activity feed. Frontend has no corresponding service.

---

## Summary of Capabilities

### ✅ **Working Flows (4/8)**
- F1: Login/Logout
- F4: View Assets List
- F5: Download Asset
- F6: Edit Metadata

### 🟡 **Partially Working (2/8)**
- F3: Upload Asset (backend works, frontend may need fixes)
- F7: Search/Filter (basic functionality exists)

### ❌ **Broken Flows (2/8)**
- F2: Change Password (missing API endpoint)
- F8: Activity History (missing user-specific API)

### Key Insights

1. **Core DAM operations work** - CRUD on documents, uploads, downloads are functional
2. **Self-service features missing** - Password change is a critical gap for user experience
3. **Configuration exposure insufficient** - Frontend cannot build dynamic forms
4. **API designed for automation** - Missing UX-focused endpoints expected by SPAs

---

**Analysis Status:** ✅ **PROBLEM SPACE FULLY EXPLICIT**
**Next Step:** API contract clarification and test plan design
**Documents Referenced:** All V3 analyses + ARCHITECTURE_GAP_REPORT.md + API_MISMATCH_FIX.md

---

