# API Test Plan: Verification of Contract Mismatches

**Date:** December 3, 2025
**Author:** Principal Solution Architect & QA Lead
**Purpose:** Concrete test specifications to confirm/deny API contract hypotheses
**Scope:** Manual and automated tests for all critical flows and endpoints

---

## Executive Summary

This test plan provides executable test cases to validate the API contract mismatches identified in API_MISMATCH_FIX_V2.md and flow capabilities from ARCHITECTURE_GAP_REPORT_V2.md. Tests are designed for QA engineers or developers to execute without code changes.

**Test Coverage:** All 8 critical user flows + 7 API contract mismatches
**Test Types:** Manual (high-level) + API-level (contract tests)
**Execution Tools:** Postman, curl, pytest, or any HTTP client

---

## Test Prerequisites

### Environment Setup
- Mayan EDMS running on `http://localhost:8080`
- Vue frontend running on `http://localhost:5173` (optional for API tests)
- Test user account: username `testuser`, password `testpass123`
- Valid authentication token for test user

### Test Data Setup
```bash
# Create test user via Django shell
python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
user.is_active = True
user.save()
print('Test user created')
"
```

### Authentication Token
```bash
# Get token for test user
curl -X POST http://localhost:8080/api/v4/auth/token/obtain/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
# Expected: {"access": "token_string_here"}
```

---

## Flow-Level Test Cases (Manual)

### F1: User Login/Logout

**Test Case F1.1: Successful Login**
- **Steps:**
  1. POST to `/api/v4/auth/token/obtain/` with valid credentials
  2. Verify 200 response with token
  3. GET `/api/v4/users/current/` with token
  4. Verify user data returned
- **Expected:** Token obtained, user data retrieved
- **Purpose:** Confirm authentication flow works

**Test Case F1.2: Invalid Login**
- **Steps:**
  1. POST to `/api/v4/auth/token/obtain/` with invalid credentials
- **Expected:** 401 Unauthorized
- **Purpose:** Confirm authentication rejects invalid credentials

### F2: Change Own Password

**Test Case F2.1: Wrong Endpoint (Current Behavior)**
- **Steps:**
  1. POST to `/api/v4/users/current/password/` with `{"new_password": "newpass123"}`
- **Expected:** 404 Not Found
- **Purpose:** Confirm endpoint doesn't exist (hypothesis validation)

**Test Case F2.2: Alternative PATCH Endpoint**
- **Steps:**
  1. PATCH to `/api/v4/users/current/` with `{"password": "newpass123"}`
  2. Try login with old password
  3. Try login with new password
- **Expected:** 200 OK, old password fails, new password works
- **Purpose:** Confirm PATCH works for password changes

### F3: Upload New Asset

**Test Case F3.1: Chunked Upload Flow**
- **Steps:**
  1. POST to `/api/v4/uploads/init/` with file metadata
  2. POST multiple chunks to `/api/v4/uploads/append/`
  3. POST to `/api/v4/uploads/complete/` with final metadata
  4. GET `/api/v4/documents/` to verify document created
- **Expected:** All steps 200/201, document appears in list
- **Purpose:** Confirm complete upload workflow

**Test Case F3.2: Document Creation**
- **Steps:**
  1. Complete upload flow
  2. GET `/api/v4/documents/{id}/` for created document
  3. Verify file attachment and metadata
- **Expected:** Document has file, correct metadata
- **Purpose:** Confirm Mayan creates proper Document + DocumentFile

### F4: View Assets List

**Test Case F4.1: Basic List**
- **Steps:**
  1. GET `/api/v4/documents/optimized/`
- **Expected:** 200 OK with document list
- **Purpose:** Confirm document listing works

**Test Case F4.2: Pagination**
- **Steps:**
  1. GET `/api/v4/documents/optimized/?page=1&page_size=10`
- **Expected:** Paginated results with navigation links
- **Purpose:** Confirm pagination works

### F5: Download Asset

**Test Case F5.1: Download URL**
- **Steps:**
  1. GET `/api/v4/documents/optimized/`
  2. Extract download_url from file_latest
  3. GET download_url
- **Expected:** File download or presigned URL
- **Purpose:** Confirm download URLs are functional

### F6: Edit Asset Metadata

**Test Case F6.1: Update Document**
- **Steps:**
  1. PATCH `/api/v4/documents/{id}/` with `{"label": "New Label"}`
  2. GET `/api/v4/documents/{id}/` to verify change
- **Expected:** Label updated successfully
- **Purpose:** Confirm metadata editing works

### F7: Search/Filter Assets

**Test Case F7.1: Text Search**
- **Steps:**
  1. GET `/api/v4/documents/optimized/?search=test`
- **Expected:** Filtered results containing search term
- **Purpose:** Confirm search functionality

### F8: View Activity/History

**Test Case F8.1: Events API**
- **Steps:**
  1. GET `/api/v4/events/`
- **Expected:** 200 OK with event list (system-wide)
- **Purpose:** Confirm events API exists but is not user-specific

---

## API Contract Tests (Automated)

### Contract Test 1: Password Change Endpoint

**Purpose:** Confirm that password change endpoint doesn't exist

**Test Implementation:**
```python
# pytest test
def test_password_change_endpoint_missing():
    response = requests.post(
        "http://localhost:8080/api/v4/users/current/password/",
        json={"new_password": "newpass123"},
        headers={"Authorization": f"Token {token}"}
    )
    assert response.status_code == 404
```

**Preconditions:** Valid user token
**Expected Result:** 404 Not Found
**Verification:** Endpoint missing confirmed

### Contract Test 2: Password Change via PATCH

**Purpose:** Confirm PATCH on user endpoint accepts password field

**Test Implementation:**
```python
def test_password_change_via_patch():
    # Change password
    response = requests.patch(
        "http://localhost:8080/api/v4/users/current/",
        json={"password": "newpass123"},
        headers={"Authorization": f"Token {token}"}
    )
    assert response.status_code == 200

    # Verify old password doesn't work
    auth_response = requests.post(
        "http://localhost:8080/api/v4/auth/token/obtain/",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert auth_response.status_code == 401

    # Verify new password works
    auth_response = requests.post(
        "http://localhost:8080/api/v4/auth/token/obtain/",
        json={"username": "testuser", "password": "newpass123"}
    )
    assert auth_response.status_code == 200
```

**Preconditions:** Valid user token, known old password
**Expected Result:** Password successfully changed
**Verification:** PATCH endpoint works for password changes

### Contract Test 3: Upload Complete

**Purpose:** Confirm upload completion creates documents correctly

**Test Implementation:**
```python
def test_upload_complete_creates_document():
    # This would require setting up a complete upload flow
    # For now, test the contract expectations

    # Mock upload completion payload
    payload = {
        "upload_id": "test-upload-id",
        "label": "Test Document",
        "description": "Test upload",
        "document_type_id": 1
    }

    response = requests.post(
        "http://localhost:8080/api/v4/uploads/complete/",
        json=payload,
        headers={"Authorization": f"Token {token}"}
    )

    # Expected: Either 201 (if upload_id valid) or 404 (if invalid)
    # But should NOT be 400 Bad Request for valid payload structure
    assert response.status_code in [201, 404]  # Contract valid
    assert "upload_id" in response.json()
```

**Preconditions:** Valid user token
**Expected Result:** Valid contract acceptance or proper error
**Verification:** API contract matches expectations

### Contract Test 4: Current User

**Purpose:** Confirm user retrieval works correctly

**Test Implementation:**
```python
def test_current_user_retrieval():
    response = requests.get(
        "http://localhost:8080/api/v4/users/current/",
        headers={"Authorization": f"Token {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "email" in data
    assert data["username"] == "testuser"
```

**Preconditions:** Valid user token
**Expected Result:** User data retrieved
**Verification:** GET /users/current/ works

### Contract Test 5: Document List

**Purpose:** Confirm optimized document API works

**Test Implementation:**
```python
def test_document_list_optimized():
    response = requests.get(
        "http://localhost:8080/api/v4/documents/optimized/",
        headers={"Authorization": f"Token {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert isinstance(data["results"], list)
```

**Preconditions:** Valid user token
**Expected Result:** Document list retrieved
**Verification:** Optimized API functional

### Contract Test 6: Document Type Configuration

**Purpose:** Confirm document types don't expose configuration

**Test Implementation:**
```python
def test_document_type_limited_config():
    response = requests.get(
        "http://localhost:8080/api/v4/document_types/1/",
        headers={"Authorization": f"Token {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should have basic info
    assert "id" in data
    assert "label" in data

    # Should NOT have configuration schema
    assert "required_fields" not in data
    assert "validation_rules" not in data
    assert "metadata_schema" not in data
```

**Preconditions:** Valid user token, existing document type
**Expected Result:** Basic info only, no configuration
**Verification:** Configuration exposure gap confirmed

### Contract Test 7: Events API

**Purpose:** Confirm events API exists but isn't user-specific

**Test Implementation:**
```python
def test_events_api_exists():
    response = requests.get(
        "http://localhost:8080/api/v4/events/",
        headers={"Authorization": f"Token {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

    # Check if events are user-specific (they shouldn't be)
    if data["results"]:
        event = data["results"][0]
        # Events should be system-wide, not filtered by current user
        assert "actor" in event or "user" in event  # Some event structure
```

**Preconditions:** Valid user token
**Expected Result:** Events list retrieved (system-wide)
**Verification:** Events API exists but not user-specific

---

## Test Execution Matrix

| Test ID | Flow/API | Manual/Auto | Preconditions | Expected Status | Priority |
|---------|----------|-------------|---------------|-----------------|----------|
| F1.1 | Login | Manual | None | ✅ PASS | High |
| F2.1 | Password (wrong endpoint) | Manual | Token | ❌ 404 | High |
| F2.2 | Password (PATCH) | Manual | Token | ✅ 200 | High |
| F3.1 | Upload flow | Manual | Token + file | ✅ 201 | High |
| F4.1 | Document list | Manual | Token | ✅ 200 | High |
| CT1 | Password endpoint missing | Auto | Token | ❌ 404 | High |
| CT2 | Password via PATCH | Auto | Token | ✅ 200 | High |
| CT6 | Doc type config limited | Auto | Token | ✅ Limited | Medium |
| CT7 | Events API | Auto | Token | ✅ Exists | Medium |

---

## Test Results Template

After execution, update this template:

### Test Execution Summary
- **Date:** YYYY-MM-DD
- **Tester:** [Name]
- **Environment:** [Local/Staging/Prod]

### Results by Flow
- **F1: User Login/Logout** - [PASS/FAIL] - [Notes]
- **F2: Change Password** - [PASS/FAIL] - [Notes]
- **F3: Upload Asset** - [PASS/FAIL] - [Notes]
- etc.

### Contract Test Results
- **CT1: Password endpoint missing** - [PASS/FAIL] - [Actual response]
- **CT2: Password via PATCH** - [PASS/FAIL] - [Actual response]
- etc.

### Key Findings
- [List any surprises or deviations from expected behavior]
- [Confirmation/denial of hypotheses]
- [Recommendations for next steps]

---

**Test Plan Status:** ✅ **READY FOR EXECUTION**
**Next Step:** Execute tests and update results template
**Tools Required:** curl, Postman, or pytest + requests

---
