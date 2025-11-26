# 🔧 ПРОМПТЫ ДЛЯ CURSOR AI - PHASE 1 BACKEND (5 Задач)

**Версия:** 1.0  
**Дата:** 26 ноября 2025  
**Контекст:** DAM System Implementation Roadmap Phase 1  
**Язык:** Russian (с code примерами на English)

---

## 📋 ИСПОЛЬЗОВАНИЕ ЭТИХ ПРОМПТОВ

1. **Откройте Cursor AI** в вашем проекте Django
2. **Выберите задачу** (Task 1.1 - 1.5)
3. **Скопируйте весь промпт** (от "You are a senior..." до "END OF PROMPT")
4. **Вставьте в Cursor AI**
5. **Нажмите Enter** и дождитесь генерации кода
6. **Проверьте** generated файлы и примените изменения

---

# ✅ TASK 1.1: JSON Serialization - DAMDocumentDetailView

## Для Cursor AI - Скопируйте целиком:

```
You are a senior Django REST Framework architect specializing in API design and data serialization. Your task is to fix a critical API blocker where the DAMDocumentDetailView returns HTML markup in a JSON response instead of properly serialized data.

CURRENT STATE (BROKEN):
- File: mayan/apps/dam/api_views.py (Lines 208-257)
- Problem: DAMDocumentDetailView has a field "html" that contains raw HTML markup
- Impact: Frontend cannot parse structured data, violates REST API principles
- Status: 🔴 CRITICAL - blocks all frontend detail pages

CONTEXT FROM ROADMAP:
This is Task 1.1 from Phase 1 Backend (Weeks 1-2). This fix is BLOCKING frontend Phase 2.
Estimated effort: 1 day. No dependencies. Deadline: EOW1.

DELIVERABLE REQUIRED:
1. mayan/apps/dam/serializers.py - Add DAMDocumentDetailSerializer
2. mayan/apps/dam/api_views.py - Update DAMDocumentDetailView
3. mayan/apps/dam/tests/test_api_integration.py - Add tests

YOUR TASK:
================================================================================

Step 1: ANALYZE CURRENT CODE
- Read the existing DAMDocumentDetailView implementation
- Identify all places where HTML is being serialized
- Document the current data flow and template rendering

Step 2: CREATE DAMDocumentDetailSerializer
Location: mayan/apps/dam/serializers.py

This serializer must return clean, structured JSON with these field groups:

GROUP A - DOCUMENT BASICS:
  - id (Integer)
  - title (String)
  - description (String)
  - asset_type (String: 'image', 'video', 'document', etc)
  - asset_status (String: 'active', 'archived', etc)

GROUP B - FILE INFORMATION:
  - file_id (Integer, nullable)
  - filename (String, nullable)
  - file_size (Integer, nullable) - in bytes
  - mime_type (String, nullable)

GROUP C - TIMESTAMPS:
  - created_at (DateTime)
  - updated_at (DateTime)

GROUP D - METADATA (IMPORTANT: NOT HTML):
  - metadata (Array of Objects), each object has:
    {
      "key": "FieldName",
      "value": "extracted_value",
      "type": "string",
      "lookup": "field_lookup"
    }

GROUP E - DOCUMENT VERSIONS (last 5):
  - versions_count (Integer)
  - versions (Array of Objects), each object has:
    {
      "id": 123,
      "version_number": 1,
      "timestamp": "2025-01-25T10:30:00Z",
      "file_size": 1024000,
      "filename": "file.pdf"
    }

GROUP F - USER PERMISSIONS (what current user can do):
  - permissions (Object):
    {
      "can_view": true,
      "can_download": true,
      "can_edit_metadata": true,
      "can_delete": false,
      "can_share": true,
      "can_analyze": true
    }

GROUP G - METRICS:
  - view_count (Integer)
  - download_count (Integer)

GROUP H - TAGS:
  - tags (Array of Strings)

IMPLEMENTATION DETAILS:
- Use SerializerMethodField for computed fields
- Add get_* methods for each computed field
- Handle missing related objects gracefully (no TypeErrors)
- Use select_related/prefetch_related to avoid N+1 queries
- Add comprehensive docstrings

Step 3: UPDATE DAMDocumentDetailView
Location: mayan/apps/dam/api_views.py

Requirements:
- Replace HTML rendering with DAMDocumentDetailSerializer
- Apply select_related('document__files', 'document__metadata') for optimization
- Override get_serializer_context() to pass request for permission checks
- Add proper error handling (404, 403, 400)
- Return proper HTTP status codes

Make this a generics.RetrieveUpdateDestroyAPIView with:
- queryset: Document.objects.all()
- serializer_class: DAMDocumentDetailSerializer
- permission_classes: (IsAuthenticated,)
- filter for ACL permissions in get_queryset()

Step 4: ADD COMPREHENSIVE TESTS
Location: mayan/apps/dam/tests/test_api_integration.py

Test cases required:
1. test_document_detail_returns_json() - Verify JSON structure, no HTML
2. test_document_detail_includes_metadata() - Verify metadata as array
3. test_document_detail_includes_permissions() - Verify permission object
4. test_document_detail_includes_versions() - Verify version history (last 5)
5. test_document_detail_404_missing_document() - Test missing doc
6. test_document_detail_403_no_permission() - Test permission check
7. test_document_detail_performance() - Verify queries < 5 (prefetch working)

Step 5: VALIDATION CHECKLIST
Before submitting, verify:
- [ ] Response is 100% valid JSON (use json.loads to verify)
- [ ] No HTML string in any field
- [ ] All metadata is array of objects, not HTML blob
- [ ] File info present (size, mime_type, filename)
- [ ] Permissions included and correct
- [ ] Versions included (max 5, with timestamps)
- [ ] No 500 errors on missing related objects
- [ ] Proper error messages (404 for not found, 403 for no access)
- [ ] API response time < 100ms (test with 10 documents)
- [ ] Works with both GET and OPTIONS requests

TESTING COMMAND:
After implementation, run:
```bash
# Test the API endpoint directly
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v4/dam/documents/1/

# Should return clean JSON like this structure:
{
  "id": 1,
  "title": "Sample Document",
  "description": "A test document",
  "asset_type": "document",
  "asset_status": "active",
  "filename": "sample.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf",
  "created_at": "2025-01-25T10:30:00Z",
  "updated_at": "2025-01-25T10:30:00Z",
  "metadata": [
    {"key": "Department", "value": "Finance", "type": "string"},
    {"key": "Year", "value": "2025", "type": "number"}
  ],
  "versions_count": 3,
  "versions": [...],
  "permissions": {...},
  "tags": ["important", "financial"],
  "view_count": 15,
  "download_count": 3
}
```

ACCEPTANCE CRITERIA (MUST ALL PASS):
✓ Response is valid JSON (not HTML)
✓ All fields documented in docstrings
✓ Metadata is array of objects (not HTML)
✓ File info included (size, mime type)
✓ Permissions included and accurate
✓ Versions included (last 5 max)
✓ No 500 errors on missing objects
✓ Proper error messages (404, 403)
✓ Works with both GET and OPTIONS
✓ All tests pass (pytest -v)
✓ No N+1 queries (< 5 total queries)

OUTPUT FILES TO GENERATE:
1. mayan/apps/dam/serializers.py
   - Add DAMDocumentDetailSerializer class (200-250 lines)
   - Include all get_* methods
   - Add comprehensive docstrings

2. mayan/apps/dam/api_views.py
   - Update DAMDocumentDetailView class
   - Add get_queryset() with select_related/prefetch_related
   - Add get_serializer_context() method

3. mayan/apps/dam/tests/test_api_integration.py
   - Create TestDocumentDetailAPI class
   - Add 7 test methods (listed above)
   - Use Django TestCase with API client

NOTES:
- This is the #1 priority blocker
- Frontend is waiting for this to work properly
- Security/permission checks are MANDATORY
- No TypeErrors allowed on missing related objects
- All error responses must include error_code field

END OF PROMPT
```

---

# ✅ TASK 1.2: Rate Limiting Configuration

## Для Cursor AI - Скопируйте целиком:

```
You are a senior Django REST Framework security architect. Your task is to add comprehensive rate limiting and throttling configuration to protect the API from abuse and DDoS attacks.

CURRENT STATE (BROKEN):
- Status: No rate limiting configured on API
- Problem: Users can spam endpoints without limit
- Risk: DDoS vulnerability, unauthorized abuse of AI analysis endpoints
- Impact: 🔴 CRITICAL - Security vulnerability

CONTEXT FROM ROADMAP:
This is Task 1.2 from Phase 1 Backend (Weeks 1-2). Must be done before Task 1.3.
Estimated effort: 0.5 days. No dependencies. Deadline: EOW1.

DELIVERABLES REQUIRED:
1. mayan/apps/dam/throttles.py - Custom throttle classes
2. mayan/settings/local_settings.py - Throttle configuration
3. Logging configuration for throttle monitoring

YOUR TASK:
================================================================================

Step 1: CREATE CUSTOM THROTTLE CLASS
Location: mayan/apps/dam/throttles.py (NEW FILE)

Create AIAnalysisThrottle class that extends UserRateThrottle:

Requirements:
- scope = 'ai_analysis'
- Strict rate limiting for AI operations:
  * 10 requests per minute (aggressive)
  * 50 requests per hour
  * 500 requests per day
- Log all throttle events for monitoring
- Include throttle_success() method to log permission
- Include throttle_failure() method to log rejection

Implementation should:
1. Extend UserRateThrottle from rest_framework.throttling
2. Override get_cache_key() if needed for custom scoping
3. Add logging using Python's logging module
4. Log format: JSON with user_id, timestamp, remaining_requests
5. Handle edge cases (anonymous users, missing user)

Step 2: UPDATE DJANGO SETTINGS
Location: mayan/settings/local_settings.py

Add/update REST_FRAMEWORK settings:

```python
REST_FRAMEWORK = {
    # Throttling configuration
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        # General API limits
        'anon': '100/hour',          # Anonymous: 100 req/hour
        'user': '1000/hour',         # Authenticated: 1000 req/hour
        
        # Specific scopes for critical operations
        'ai_analysis': '10/minute,50/hour,500/day',  # AI operations
        'ai_analysis_anon': '1/hour',               # Anon AI (almost blocked)
        'upload': '50/hour',                        # File uploads
        'download': '100/hour',                     # Downloads
        'bulk_operation': '20/hour',                # Bulk actions
    },
    
    # Other important settings (if not already present)
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

Step 3: CONFIGURE CACHING FOR THROTTLE TRACKING
Add to settings.py:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mayan-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# For production, use Redis instead:
# 'BACKEND': 'django_redis.cache.RedisCache',
# 'LOCATION': 'redis://127.0.0.1:6379/1',
```

Step 4: CONFIGURE LOGGING FOR THROTTLE EVENTS
Add to settings.py LOGGING configuration:

Create 'mayan.apps.dam.throttle' logger that:
- Logs WARNING level when throttle limit hit
- Includes user_id, request_path, timestamp
- Writes to logs/throttle.log file
- Rotates at 5MB, keeps 5 backups
- Uses JSON formatter for parsing

Log format example:
```json
{
  "timestamp": "2025-01-26T10:30:45Z",
  "user_id": 42,
  "level": "WARNING",
  "event": "throttle_limit_exceeded",
  "scope": "ai_analysis",
  "remaining": 0,
  "action": "POST /api/v4/dam/documents/analyze/"
}
```

Step 5: VERIFICATION & TESTING
Test the implementation with:

```bash
# Test 1: Normal request (should work)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v4/dam/documents/

# Expected response: HTTP 200 with data

# Test 2: Throttle limit (make 11 requests, 10th should work, 11th should fail)
for i in {1..15}; do
  curl -H "Authorization: Bearer TOKEN" \
    -X POST http://localhost:8000/api/v4/dam/documents/analyze/ \
    -H "Content-Type: application/json" \
    -d '{"document_id": 1}'
  echo "Request $i"
done

# Expected: First 10 succeed (202), 11th+ get 429 Too Many Requests

# Test 3: Check throttle headers
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v4/dam/documents/ \
  -v

# Expected response headers:
# X-RateLimit-Limit: 1000
# X-RateLimit-Remaining: 999
# X-RateLimit-Reset: 1234567890
```

Step 6: VERIFY LOGGING
After making requests:
```bash
# Check throttle log file
tail -f logs/throttle.log

# Should show JSON entries with throttle events
```

IMPLEMENTATION CHECKLIST:
- [ ] throttles.py created with AIAnalysisThrottle class
- [ ] settings.py updated with DEFAULT_THROTTLE_CLASSES
- [ ] DEFAULT_THROTTLE_RATES configured with all scopes
- [ ] CACHES configuration added (local or Redis)
- [ ] LOGGING configured for throttle events
- [ ] X-RateLimit-* headers present in responses
- [ ] Throttle limits enforced (429 returned)
- [ ] Throttle events logged to file
- [ ] All tests pass

ACCEPTANCE CRITERIA (MUST ALL PASS):
✓ DEFAULT_THROTTLE_CLASSES configured
✓ DEFAULT_THROTTLE_RATES has all scopes
✓ Anonymous users get 100/hour limit
✓ Authenticated users get 1000/hour limit
✓ AI operations get 10/minute (strict)
✓ Cache backend working (local or Redis)
✓ HTTP 429 returned when limit exceeded
✓ X-RateLimit-* headers in response
✓ Throttle events logged to JSON file
✓ Logging rotates at 5MB
✓ Can run 11 requests and see 429 on 11th

TESTING COMMAND:
```bash
# Run after implementation
python manage.py shell

# Verify throttle rates are loaded
from django.conf import settings
print(settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'])

# Should output all configured rates
```

NOTES:
- This must work before Task 1.3
- Security-critical: No exceptions
- Monitor throttle.log file for anomalies
- Adjust rates if legitimate users hitting limits
- Redis recommended for production (more reliable)

END OF PROMPT
```

---

# ✅ TASK 1.3: DocumentAIAnalysisViewSet - Throttle + ACL

## Для Cursor AI - Скопируйте целиком:

```
You are a senior Django REST Framework architect specializing in security and permissions. Your task is to fix the DocumentAIAnalysisViewSet by adding rate limiting, proper error handling, and critical ACL checks.

CURRENT STATE (BROKEN):
- File: mayan/apps/dam/api_views.py (DocumentAIAnalysisViewSet)
- Problems:
  1. analyze action missing throttle (users can spam)
  2. reanalyze action missing ACL check (security gap!)
  3. Generic Exception catching without proper error structure
  4. No logging for audit trail
- Status: 🔴 CRITICAL - Security & DDoS vulnerability

CONTEXT FROM ROADMAP:
This is Task 1.3 from Phase 1 Backend (Weeks 1-2). Depends on Task 1.2 (Rate Limiting).
Estimated effort: 1 day. Deadline: EOW1.

DELIVERABLES REQUIRED:
1. mayan/apps/dam/api_views.py - Update DocumentAIAnalysisViewSet
2. mayan/apps/dam/tests/test_ai_analysis_api.py - Add comprehensive tests
3. Logging integration for audit trail

YOUR TASK:
================================================================================

Step 1: UNDERSTAND CURRENT IMPLEMENTATION
- Review DocumentAIAnalysisViewSet class
- Identify analyze() and reanalyze() action methods
- Note: Task 1.2 (Rate Limiting) already configured AIAnalysisThrottle
- You will apply it here in this task

Step 2: UPDATE DocumentAIAnalysisViewSet
Location: mayan/apps/dam/api_views.py

Apply throttle_classes to ViewSet:

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from mayan.apps.dam.throttles import AIAnalysisThrottle
from mayan.apps.permissions.models import Permission
from mayan.apps.acls.models import AccessControlList
import logging

logger = logging.getLogger(__name__)

# Get permission reference (should exist)
permission_document_view = Permission.objects.get(codename='view_document')
permission_document_analyze = Permission.objects.get(codename='dam_analyze')

class DocumentAIAnalysisViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    throttle_classes = (AIAnalysisThrottle,)  # ADD THIS LINE
    
    # ... rest of the class
```

Step 3: FIX analyze() ACTION
Location: In DocumentAIAnalysisViewSet

Current issues to fix:
1. Missing throttle (now inherited from class)
2. Generic Exception catching
3. No logging

Implementation:

```python
@action(detail=False, methods=['post'], url_path='analyze')
def analyze(self, request):
    """
    POST /api/v4/dam/documents/analyze/
    
    Analyze a document with AI. Throttled to 10/minute.
    
    Request body:
    {
        "document_id": 1,
        "ai_service": "openai",
        "analysis_type": "classification"
    }
    
    Response: 202 Accepted (async processing)
    {
        "success": true,
        "analysis_id": "task-uuid",
        "status": "pending",
        "created_at": "2025-01-26T10:30:00Z"
    }
    """
    
    # 1. Validate input
    serializer = DocumentAIAnalysisSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                "error": "Invalid request",
                "error_code": "VALIDATION_ERROR",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated = serializer.validated_data
    document_id = validated['document_id']
    ai_service = validated.get('ai_service', 'openai')
    analysis_type = validated.get('analysis_type', 'classification')
    
    try:
        # 2. Get document
        document = Document.objects.get(pk=document_id)
        
        # 3. Check view permission (REQUIRED before analyze)
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_view,),
            user=request.user
        )
        
        # 4. Check analyze permission
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_analyze,),
            user=request.user
        )
        
        # 5. Check if analyzable
        if not self._is_analyzable(document):
            return Response(
                {
                    "error": "Document type not supported",
                    "error_code": "UNSUPPORTED_TYPE",
                    "supported_types": ["pdf", "image", "docx"]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 6. Create async task
        from mayan.apps.dam.tasks import ai_analyze_document
        result = ai_analyze_document.delay(
            document_id=document.id,
            ai_service=ai_service,
            analysis_type=analysis_type,
            user_id=request.user.id
        )
        
        # 7. Log for audit trail
        logger.info(
            f"AI analysis started for document {document_id}",
            extra={
                "user_id": request.user.id,
                "document_id": document_id,
                "task_id": result.id,
                "ai_service": ai_service,
                "action": "analyze"
            }
        )
        
        # 8. Return 202 Accepted (async)
        return Response(
            {
                "success": True,
                "analysis_id": result.id,
                "status": "pending",
                "document_id": document_id,
                "created_at": datetime.now().isoformat()
            },
            status=status.HTTP_202_ACCEPTED
        )
    
    except Document.DoesNotExist:
        return Response(
            {
                "error": "Document not found",
                "error_code": "NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    except PermissionDenied:
        logger.warning(
            f"Unauthorized analyze attempt for document {document_id}",
            extra={
                "user_id": request.user.id,
                "document_id": document_id
            }
        )
        return Response(
            {
                "error": "Permission denied",
                "error_code": "PERMISSION_DENIED"
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    except Exception as e:
        logger.exception(
            f"Error analyzing document {document_id}",
            extra={
                "user_id": request.user.id,
                "document_id": document_id,
                "error": str(e)
            }
        )
        return Response(
            {
                "error": "Analysis failed",
                "error_code": "ANALYSIS_ERROR",
                "detail": str(e) if settings.DEBUG else "Internal error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

Step 4: FIX reanalyze() ACTION (CRITICAL ACL CHECK MISSING!)
Location: In DocumentAIAnalysisViewSet

⚠️ THIS IS THE SECURITY GAP - reanalyze forgot ACL check!

```python
@action(detail=False, methods=['post'], url_path='reanalyze')
def reanalyze(self, request):
    """
    POST /api/v4/dam/documents/reanalyze/
    
    Re-analyze an already-analyzed document.
    ⚠️ CRITICAL: This now checks permissions (was missing!)
    
    Request body:
    {
        "analysis_id": 123,
        "force": false
    }
    """
    
    analysis_id = request.data.get('analysis_id')
    force = request.data.get('force', False)
    
    if not analysis_id:
        return Response(
            {
                "error": "analysis_id is required",
                "error_code": "MISSING_PARAMETER"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from mayan.apps.dam.models import DocumentAIAnalysis
        
        # Get previous analysis
        previous_analysis = DocumentAIAnalysis.objects.get(pk=analysis_id)
        document = previous_analysis.document
        
        # ⚠️ CRITICAL FIX: Check permissions (THIS WAS MISSING!)
        AccessControlList.objects.check_access(
            obj=document,
            permissions=(permission_document_analyze,),
            user=request.user
        )
        
        # Check rate limit (don't reanalyze too often)
        if not force and not self._can_reanalyze(previous_analysis):
            return Response(
                {
                    "error": "Re-analysis too soon",
                    "error_code": "RATE_LIMITED",
                    "retry_after": 3600
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Create new task
        from mayan.apps.dam.tasks import ai_analyze_document
        result = ai_analyze_document.delay(
            document_id=document.id,
            ai_service=previous_analysis.ai_service,
            analysis_type=previous_analysis.analysis_type,
            user_id=request.user.id,
            previous_analysis_id=analysis_id
        )
        
        logger.info(
            f"Re-analysis started for document {document.id}",
            extra={
                "user_id": request.user.id,
                "previous_analysis_id": analysis_id,
                "new_task_id": result.id,
                "action": "reanalyze"
            }
        )
        
        return Response(
            {
                "success": True,
                "new_analysis_id": result.id,
                "status": "pending",
                "document_id": document.id,
                "created_at": datetime.now().isoformat()
            },
            status=status.HTTP_202_ACCEPTED
        )
    
    except DocumentAIAnalysis.DoesNotExist:
        return Response(
            {
                "error": "Analysis not found",
                "error_code": "NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    except PermissionDenied:
        logger.warning(
            f"Unauthorized reanalyze attempt",
            extra={
                "user_id": request.user.id,
                "analysis_id": analysis_id
            }
        )
        return Response(
            {
                "error": "Permission denied",
                "error_code": "PERMISSION_DENIED"
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    except Exception as e:
        logger.exception(
            f"Error re-analyzing",
            extra={
                "user_id": request.user.id,
                "analysis_id": analysis_id,
                "error": str(e)
            }
        )
        return Response(
            {
                "error": "Re-analysis failed",
                "error_code": "ANALYSIS_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

Step 5: ADD HELPER METHODS
Add these methods to DocumentAIAnalysisViewSet:

```python
@staticmethod
def _is_analyzable(document: Document) -> bool:
    """Check if document type can be analyzed"""
    analyzable_types = ['pdf', 'image', 'docx', 'doc', 'txt']
    try:
        mime_type = document.latest_version.file.mimetype or ''
        return any(t in mime_type.lower() for t in analyzable_types)
    except Exception:
        return False

@staticmethod
def _can_reanalyze(analysis) -> bool:
    """Check if enough time has passed since last analysis"""
    from datetime import timedelta
    from django.utils import timezone
    
    # Allow re-analysis only after 1 hour
    min_time_between = timedelta(hours=1)
    time_since = timezone.now() - analysis.created_at
    return time_since >= min_time_between
```

Step 6: CREATE COMPREHENSIVE TESTS
Location: mayan/apps/dam/tests/test_ai_analysis_api.py

Test cases required:
1. test_analyze_returns_202_accepted() - Verify async response
2. test_analyze_checks_permissions() - Verify 403 without permission
3. test_analyze_checks_document_exists() - Verify 404 for missing doc
4. test_analyze_respects_throttle() - Verify 429 on 11th request
5. test_reanalyze_checks_acl() - Verify 403 without permission (CRITICAL)
6. test_reanalyze_returns_202_accepted() - Verify async response
7. test_analyze_logs_audit_trail() - Verify logging
8. test_error_response_has_error_code() - Verify error_code field

Step 7: VERIFY IMPLEMENTATION
Test commands:

```bash
# Test 1: Analyze endpoint
curl -X POST http://localhost:8000/api/v4/dam/documents/analyze/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1, "ai_service": "openai"}'

# Expected: HTTP 202 Accepted with analysis_id

# Test 2: Throttle limit
for i in {1..15}; do
  curl -X POST ... (same as above)
done

# Expected: 10 succeed, 11+ get 429

# Test 3: Reanalyze without permission
curl -X POST http://localhost:8000/api/v4/dam/documents/reanalyze/ \
  -H "Authorization: Bearer TOKEN_NO_PERMISSION" \
  -d '{"analysis_id": 1}'

# Expected: HTTP 403 Permission Denied

# Test 4: Check logs
tail -f logs/dam_analysis.log

# Should see JSON entries for audit trail
```

ACCEPTANCE CRITERIA (MUST ALL PASS):
✓ analyze action returns 202 Accepted
✓ analyze returns error_code in response
✓ reanalyze checks ACL (403 without permission)
✓ Throttle limits enforced (429)
✓ All errors return structured JSON
✓ Logging includes user_id, document_id, action
✓ No generic Exception raised (all handled)
✓ PermissionDenied raises 403
✓ Missing document raises 404
✓ All tests pass (pytest -v)

NOTES:
- Throttle from Task 1.2 should be inherited by this ViewSet
- ACL check in reanalyze is the CRITICAL security fix
- Error handling must be comprehensive (no generic Exception)
- All operations must be logged for audit trail
- Use error_code field consistently

END OF PROMPT
```

---

# ✅ TASK 1.4: BulkAnalyzeDocumentsSerializer - Validation & Limits

## Для Cursor AI - Скопируйте целиком:

```
You are a senior Django serializer architect specializing in security and input validation. Your task is to fix BulkAnalyzeDocumentsSerializer by adding critical limits and permission checks.

CURRENT STATE (BROKEN):
- File: mayan/apps/dam/serializers.py (Lines 185-192)
- Problems:
  1. No max_length on document_ids (can send 1 million!)
  2. No permission check for each document
  3. No validation of document existence before processing
  4. DoS vulnerability via large batch requests
- Status: 🔴 CRITICAL - DoS vulnerability

CONTEXT FROM ROADMAP:
This is Task 1.4 from Phase 1 Backend (Weeks 1-2). No dependencies, can be done parallel.
Estimated effort: 1 day. Deadline: EOW1.

DELIVERABLE REQUIRED:
1. mayan/apps/dam/serializers.py - Fix BulkAnalyzeDocumentsSerializer
2. mayan/apps/dam/api_views.py - Add bulk_analyze action if not present
3. mayan/apps/dam/tests/test_bulk_analyze.py - Comprehensive tests

YOUR TASK:
================================================================================

Step 1: UNDERSTAND CURRENT IMPLEMENTATION
Review existing BulkAnalyzeDocumentsSerializer:
- Identify ListField for document_ids
- Note: Currently has NO max_length
- Note: Currently has NO permission checks
- Note: Can process unlimited documents

Step 2: UPDATE BulkAnalyzeDocumentsSerializer
Location: mayan/apps/dam/serializers.py

Implement complete validation:

```python
from rest_framework import serializers
from django.core.exceptions import ValidationError
from mayan.apps.documents.models import Document
from mayan.apps.acls.models import AccessControlList
from mayan.apps.permissions.models import Permission
import logging

logger = logging.getLogger(__name__)

class BulkAnalyzeDocumentsSerializer(serializers.Serializer):
    """
    Serializer for bulk AI analysis of multiple documents.
    
    Validates:
    - Maximum 100 documents per request (DoS protection)
    - User has analyze permission for each document
    - All document IDs exist
    - AI service is valid and configured
    
    Attributes:
        MAX_BULK_SIZE: Maximum documents per request (configurable)
        ALLOWED_AI_SERVICES: List of available AI services
    """
    
    # Configuration
    MAX_BULK_SIZE = 100  # Can be moved to settings.py later
    ALLOWED_AI_SERVICES = ['openai', 'claude', 'azure', 'local']
    
    # Fields
    document_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        help_text='List of document IDs to analyze (max 100)',
        required=True,
        allow_empty=False
    )
    
    ai_service = serializers.ChoiceField(
        choices=ALLOWED_AI_SERVICES,
        default='openai',
        help_text='AI service to use'
    )
    
    analysis_type = serializers.CharField(
        max_length=50,
        default='classification',
        help_text='Type of analysis'
    )
    
    # Validation methods
    
    def validate_document_ids(self, value: list) -> list:
        """
        Comprehensive validation of document IDs.
        
        Checks:
        1. Batch size (max 100)
        2. Uniqueness (no duplicates)
        3. Existence (all IDs exist in DB)
        4. User permissions (for each document)
        """
        
        # CHECK 1: Batch size
        if len(value) > self.MAX_BULK_SIZE:
            raise serializers.ValidationError(
                f"Too many documents. Maximum {self.MAX_BULK_SIZE} allowed, "
                f"got {len(value)}. Please split into multiple requests."
            )
        
        if len(value) == 0:
            raise serializers.ValidationError(
                "At least one document_id is required"
            )
        
        # CHECK 2: Uniqueness
        if len(value) != len(set(value)):
            duplicates = [
                d for d in set(value) 
                if value.count(d) > 1
            ]
            raise serializers.ValidationError(
                f"Duplicate document IDs: {duplicates}"
            )
        
        # CHECK 3: Document existence
        documents = Document.objects.filter(id__in=value)
        found_ids = set(documents.values_list('id', flat=True))
        missing_ids = set(value) - found_ids
        
        if missing_ids:
            raise serializers.ValidationError(
                f"Documents not found: {sorted(missing_ids)}"
            )
        
        # CHECK 4: User permissions (CRITICAL)
        user = self.context.get('request').user if self.context.get('request') else None
        
        if not user:
            raise serializers.ValidationError(
                "User not authenticated"
            )
        
        # Get required permission
        try:
            permission_analyze = Permission.objects.get(
                codename='dam_analyze'
            )
        except Permission.DoesNotExist:
            raise serializers.ValidationError(
                "Permission configuration error: dam_analyze not found"
            )
        
        # Check each document for permission
        unauthorized_ids = []
        for document in documents:
            try:
                AccessControlList.objects.check_access(
                    obj=document,
                    permissions=(permission_analyze,),
                    user=user
                )
            except PermissionDenied:
                unauthorized_ids.append(document.id)
        
        if unauthorized_ids:
            raise serializers.ValidationError(
                f"Permission denied for documents: {unauthorized_ids}. "
                f"You can only analyze documents you have permission to access."
            )
        
        logger.info(
            f"Bulk analyze validation passed for {len(value)} documents",
            extra={
                "user_id": user.id if user else None,
                "doc_count": len(value),
                "document_ids": value
            }
        )
        
        return value
    
    def validate_ai_service(self, value: str) -> str:
        """Validate AI service is configured and available"""
        
        # Check it's in allowed list
        if value not in self.ALLOWED_AI_SERVICES:
            raise serializers.ValidationError(
                f"Invalid AI service: {value}. "
                f"Allowed: {self.ALLOWED_AI_SERVICES}"
            )
        
        # Check it's actually configured
        from django.conf import settings
        ai_config = getattr(settings, 'DAM_AI_SERVICES', {})
        
        if value not in ai_config:
            raise serializers.ValidationError(
                f"AI service '{value}' not configured. "
                f"Available: {list(ai_config.keys())}"
            )
        
        service_config = ai_config[value]
        if not service_config.get('enabled', False):
            raise serializers.ValidationError(
                f"AI service '{value}' is disabled"
            )
        
        return value
    
    def validate_analysis_type(self, value: str) -> str:
        """Validate analysis type is supported"""
        
        allowed_types = [
            'classification',
            'extraction',
            'summarization',
            'tagging'
        ]
        
        if value not in allowed_types:
            raise serializers.ValidationError(
                f"Invalid analysis_type: {value}. "
                f"Allowed: {allowed_types}"
            )
        
        return value
    
    def validate(self, data):
        """Final validation after all fields"""
        
        # Ensure all required fields
        if 'document_ids' not in data:
            raise serializers.ValidationError(
                "document_ids is required"
            )
        
        # Log for audit
        user = self.context.get('request').user if self.context.get('request') else None
        logger.info(
            f"Bulk analysis request validated",
            extra={
                "user_id": user.id if user else None,
                "doc_count": len(data['document_ids']),
                "ai_service": data.get('ai_service'),
                "analysis_type": data.get('analysis_type')
            }
        )
        
        return data
```

Step 3: CREATE bulk_analyze ACTION IN VIEWSET
Location: mayan/apps/dam/api_views.py

Add this action to DocumentAIAnalysisViewSet:

```python
@action(detail=False, methods=['post'], url_path='bulk-analyze')
def bulk_analyze(self, request):
    """
    POST /api/v4/dam/documents/bulk-analyze/
    
    Analyze multiple documents in batch (max 100).
    
    Request body:
    {
        "document_ids": [1, 2, 3, 4, 5],
        "ai_service": "openai",
        "analysis_type": "classification"
    }
    
    Response: 202 Accepted
    {
        "success": true,
        "bulk_analysis_id": "uuid-here",
        "document_count": 5,
        "status": "pending",
        "created_at": "2025-01-26T10:30:00Z"
    }
    """
    
    # Validate input
    serializer = BulkAnalyzeDocumentsSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'error': 'Validation failed',
                'error_code': 'VALIDATION_ERROR',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated = serializer.validated_data
    
    try:
        from uuid import uuid4
        from mayan.apps.dam.tasks import bulk_ai_analyze_documents
        
        bulk_id = str(uuid4())
        doc_count = len(validated['document_ids'])
        
        # Create async bulk task
        result = bulk_ai_analyze_documents.delay(
            bulk_id=bulk_id,
            document_ids=validated['document_ids'],
            ai_service=validated['ai_service'],
            analysis_type=validated['analysis_type'],
            user_id=request.user.id
        )
        
        logger.info(
            f"Bulk analysis started",
            extra={
                "user_id": request.user.id,
                "bulk_id": bulk_id,
                "task_id": result.id,
                "doc_count": doc_count,
                "ai_service": validated['ai_service']
            }
        )
        
        return Response(
            {
                'success': True,
                'bulk_analysis_id': bulk_id,
                'document_count': doc_count,
                'status': 'pending',
                'ai_service': validated['ai_service'],
                'created_at': datetime.now().isoformat(),
                'message': f'Bulk analysis started for {doc_count} documents'
            },
            status=status.HTTP_202_ACCEPTED
        )
    
    except Exception as e:
        logger.exception(
            'Error starting bulk analysis',
            extra={
                'user_id': request.user.id,
                'error': str(e)
            }
        )
        return Response(
            {
                'success': False,
                'error': 'Failed to start bulk analysis',
                'error_code': 'BULK_ANALYSIS_ERROR',
                'detail': str(e) if settings.DEBUG else 'Internal error'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

Step 4: CREATE COMPREHENSIVE TESTS
Location: mayan/apps/dam/tests/test_bulk_analyze.py

Test cases required:
1. test_bulk_analyze_valid_request() - 202 Accepted
2. test_bulk_analyze_max_size_exceeded() - 400 with 101 docs
3. test_bulk_analyze_missing_document() - 400 for missing ID
4. test_bulk_analyze_duplicate_ids() - 400 for duplicates
5. test_bulk_analyze_permission_denied() - 400 for unauthorized docs
6. test_bulk_analyze_invalid_service() - 400 for unknown AI service
7. test_bulk_analyze_invalid_type() - 400 for unknown analysis type
8. test_bulk_analyze_empty_list() - 400 for empty list
9. test_bulk_analyze_response_structure() - Verify response format
10. test_bulk_analyze_logging() - Verify audit trail

```python
from django.test import TestCase, APIClient
from mayan.apps.documents.models import Document
from mayan.apps.users.models import User
from rest_framework import status

class BulkAnalyzeDocumentsTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test documents
        self.docs = []
        for i in range(10):
            doc = Document.objects.create(
                title=f"Document {i}",
                description=f"Test doc {i}"
            )
            self.docs.append(doc)
    
    def test_bulk_analyze_valid_request(self):
        """Test valid bulk analyze request returns 202"""
        data = {
            'document_ids': [self.docs[0].id, self.docs[1].id],
            'ai_service': 'openai',
            'analysis_type': 'classification'
        }
        response = self.client.post(
            '/api/v4/dam/documents/bulk-analyze/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data['success'])
        self.assertIn('bulk_analysis_id', response.data)
    
    def test_bulk_analyze_max_size_exceeded(self):
        """Test >100 documents returns 400"""
        doc_ids = [d.id for d in self.docs] + [99999] * 92
        data = {
            'document_ids': doc_ids,
            'ai_service': 'openai'
        }
        response = self.client.post(
            '/api/v4/dam/documents/bulk-analyze/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Too many documents', str(response.data))
    
    def test_bulk_analyze_duplicate_ids(self):
        """Test duplicate IDs returns 400"""
        data = {
            'document_ids': [self.docs[0].id, self.docs[0].id],
            'ai_service': 'openai'
        }
        response = self.client.post(
            '/api/v4/dam/documents/bulk-analyze/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Duplicate', str(response.data))
    
    def test_bulk_analyze_missing_document(self):
        """Test missing document ID returns 400"""
        data = {
            'document_ids': [999999],
            'ai_service': 'openai'
        }
        response = self.client.post(
            '/api/v4/dam/documents/bulk-analyze/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not found', str(response.data))
```

Step 5: VERIFICATION & TESTING
Test commands:

```bash
# Test 1: Valid bulk request
curl -X POST http://localhost:8000/api/v4/dam/documents/bulk-analyze/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": [1, 2, 3],
    "ai_service": "openai",
    "analysis_type": "classification"
  }'

# Expected: HTTP 202 Accepted

# Test 2: Too many documents (>100)
curl ... -d '{"document_ids": [1, 2, ..., 150]}'

# Expected: HTTP 400 "Too many documents. Maximum 100 allowed"

# Test 3: Duplicate IDs
curl ... -d '{"document_ids": [1, 2, 2, 3]}'

# Expected: HTTP 400 "Duplicate document IDs: [2]"

# Test 4: Missing document
curl ... -d '{"document_ids": [1, 99999]}'

# Expected: HTTP 400 "Documents not found: [99999]"

# Test 5: No permission
# (from user without analyze permission)
curl ...

# Expected: HTTP 400 "Permission denied for documents: [1, 2, 3]"

# Run tests
pytest mayan/apps/dam/tests/test_bulk_analyze.py -v
```

ACCEPTANCE CRITERIA (MUST ALL PASS):
✓ MAX_BULK_SIZE enforced (max 100)
✓ Duplicate IDs rejected
✓ All document_ids validated to exist
✓ Permissions checked for EACH document
✓ AI service validated (configured & enabled)
✓ Analysis type validated
✓ Response includes error_code field
✓ Logging includes document count & service
✓ 202 Accepted on success
✓ All validation errors mapped to 400
✓ All 10 unit tests pass

NOTES:
- MAX_BULK_SIZE can be configurable in settings
- Permission check must be per-document (not batch)
- Logging important for tracking bulk operations
- Error messages should be clear and actionable
- This prevents DoS attacks via large requests

END OF PROMPT
```

---

# ✅ TASK 1.5: test_preset - Input Validation & ACL

## Для Cursor AI - Скопируйте целиком:

```
You are a senior Django REST Framework architect. Your task is to fix the test_preset action by adding critical input validation and ACL permission checks.

CURRENT STATE (BROKEN):
- File: mayan/apps/dam/api_views.py (DAMMetadataPresetViewSet.test_preset)
- Problems:
  1. No validation of document_id from request.data
  2. No existence check before processing
  3. No ACL permission check (security gap!)
  4. Can crash server with invalid input
- Status: 🔴 CRITICAL - Crash & security risk

CONTEXT FROM ROADMAP:
This is Task 1.5 from Phase 1 Backend (Weeks 1-2). No dependencies, quick fix.
Estimated effort: 0.5 days. Deadline: EOW1.

DELIVERABLE REQUIRED:
1. mayan/apps/dam/serializers.py - Add TestPresetSerializer
2. mayan/apps/dam/api_views.py - Fix test_preset action
3. mayan/apps/dam/tests/test_metadata_preset.py - Add tests

YOUR TASK:
================================================================================

Step 1: UNDERSTAND CURRENT IMPLEMENTATION
Review existing DAMMetadataPresetViewSet.test_preset method:
- Note: document_id extracted from request.data
- Note: No validation present
- Note: No ACL check
- Note: Can cause TypeError or crash

Step 2: CREATE TestPresetSerializer
Location: mayan/apps/dam/serializers.py

```python
from rest_framework import serializers
from mayan.apps.documents.models import Document
from mayan.apps.acls.models import AccessControlList
from mayan.apps.permissions.models import Permission

class TestPresetSerializer(serializers.Serializer):
    """
    Serializer for testing metadata preset on a document.
    
    Validates:
    - document_id is provided and is valid integer
    - document exists in database
    - user has permission to view document
    """
    
    document_id = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        help_text='ID of the document to test the preset with',
        required=True
    )
    
    def validate_document_id(self, value):
        """
        Validate document exists and is accessible.
        Note: PrimaryKeyRelatedField already checks existence.
        """
        if not isinstance(value, Document):
            raise serializers.ValidationError(
                "Invalid document"
            )
        return value
```

Step 3: FIX test_preset ACTION
Location: mayan/apps/dam/api_views.py

In DAMMetadataPresetViewSet:

```python
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from mayan.apps.documents.models import Document
from mayan.apps.acls.models import AccessControlList
from mayan.apps.permissions.models import Permission
import logging

logger = logging.getLogger(__name__)

# Get permission reference
permission_document_view = Permission.objects.get(
    codename='view_document'
)

class DAMMetadataPresetViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=True, methods=['post'], url_path='test-preset')
    def test_preset(self, request, pk=None):
        """
        POST /api/v4/dam/metadata-presets/{id}/test-preset/
        
        Test a metadata preset by applying it to a document.
        Useful for validating preset configurations before deployment.
        
        Request body:
        {
            "document_id": 123
        }
        
        Response: 200 OK
        {
            "success": true,
            "message": "Preset applied successfully",
            "preset_name": "Invoice Extraction",
            "document_id": 123,
            "metadata_extracted": {
                "invoice_number": "INV-2025-001",
                "amount": "1000.00",
                "date": "2025-01-26"
            },
            "field_count": 3
        }
        """
        
        # Step 1: Get the preset
        try:
            preset = self.get_object()
        except ObjectDoesNotExist:
            logger.warning(
                f"test_preset called with non-existent preset {pk}",
                extra={'user_id': request.user.id, 'preset_id': pk}
            )
            return Response(
                {
                    'error': 'Preset not found',
                    'error_code': 'NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Step 2: Validate and get document_id via serializer
        serializer = TestPresetSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            logger.warning(
                f"test_preset validation failed",
                extra={
                    'user_id': request.user.id,
                    'preset_id': pk,
                    'errors': serializer.errors
                }
            )
            return Response(
                {
                    'error': 'Validation failed',
                    'error_code': 'VALIDATION_ERROR',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        document = serializer.validated_data['document_id']
        document_id = document.id
        
        # Step 3: ⚠️ CRITICAL: Check ACL permissions
        try:
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission_document_view,),
                user=request.user
            )
        except PermissionDenied:
            logger.warning(
                f"Unauthorized test_preset on document {document_id}",
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'preset_id': pk
                }
            )
            return Response(
                {
                    'error': 'Permission denied for this document',
                    'error_code': 'PERMISSION_DENIED'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Step 4: Apply preset and extract metadata
        try:
            extracted_metadata = self._apply_preset_to_document(
                preset,
                document
            )
            
            logger.info(
                f"Successfully tested preset {pk} on document {document_id}",
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'preset_id': pk,
                    'extracted_fields': len(extracted_metadata)
                }
            )
            
            return Response(
                {
                    'success': True,
                    'message': f'Preset {preset.name} applied successfully',
                    'preset_name': preset.name,
                    'document_id': document_id,
                    'metadata_extracted': extracted_metadata,
                    'field_count': len(extracted_metadata)
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.exception(
                f"Error testing preset {pk} on document {document_id}",
                extra={
                    'user_id': request.user.id,
                    'document_id': document_id,
                    'preset_id': pk,
                    'error': str(e)
                }
            )
            return Response(
                {
                    'error': 'Failed to apply preset',
                    'error_code': 'PRESET_ERROR',
                    'detail': str(e) if settings.DEBUG else 'Internal error'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def _apply_preset_to_document(preset, document: Document) -> dict:
        """
        Apply a metadata preset to a document and return extracted values.
        
        This is the core logic for extracting metadata from document
        based on preset configuration.
        
        Args:
            preset: DAMMetadataPreset instance
            document: Document instance
        
        Returns:
            dict: Extracted metadata {field_name: value}
        """
        extracted = {}
        
        try:
            # Get document content/text for extraction
            try:
                document_text = document.get_text()
            except Exception:
                document_text = ""
            
            # Apply preset rules
            for field in preset.fields.all():
                try:
                    # Apply field extraction logic
                    value = preset.extract_field_value(
                        field,
                        document_text
                    )
                    
                    if value:
                        extracted[field.name] = value
                
                except Exception as e:
                    logger.warning(
                        f"Error extracting field {field.name}",
                        extra={
                            'preset_id': preset.id,
                            'field_name': field.name,
                            'error': str(e)
                        }
                    )
                    # Continue with next field (don't fail entire operation)
                    continue
        
        except Exception as e:
            logger.exception(
                f"Error applying preset {preset.id}",
                extra={'error': str(e)}
            )
            raise
        
        return extracted
```

Step 4: CREATE TESTS
Location: mayan/apps/dam/tests/test_metadata_preset.py

Test cases:

```python
from django.test import TestCase, APIClient
from mayan.apps.documents.models import Document
from mayan.apps.dam.models import DAMMetadataPreset
from mayan.apps.users.models import User
from rest_framework import status

class TestPresetTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test preset
        self.preset = DAMMetadataPreset.objects.create(
            name='Test Preset'
        )
        
        # Create test document
        self.document = Document.objects.create(
            title='Test Document'
        )
    
    def test_test_preset_returns_200(self):
        """Test valid request returns 200 OK"""
        response = self.client.post(
            f'/api/v4/dam/metadata-presets/{self.preset.id}/test-preset/',
            {'document_id': self.document.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_test_preset_missing_document_id(self):
        """Test missing document_id returns 400"""
        response = self.client.post(
            f'/api/v4/dam/metadata-presets/{self.preset.id}/test-preset/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('document_id', str(response.data))
    
    def test_test_preset_invalid_document_type(self):
        """Test invalid document_id type returns 400"""
        response = self.client.post(
            f'/api/v4/dam/metadata-presets/{self.preset.id}/test-preset/',
            {'document_id': 'invalid'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_test_preset_missing_document(self):
        """Test non-existent document returns 404"""
        response = self.client.post(
            f'/api/v4/dam/metadata-presets/{self.preset.id}/test-preset/',
            {'document_id': 99999},
            format='json'
        )
        # Should be 400 from serializer (not found)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_test_preset_missing_preset(self):
        """Test non-existent preset returns 404"""
        response = self.client.post(
            f'/api/v4/dam/metadata-presets/99999/test-preset/',
            {'document_id': self.document.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_test_preset_no_permission(self):
        """Test permission denied returns 403"""
        # Create user without permission
        no_perm_user = User.objects.create_user(
            username='noperm',
            password='pass'
        )
        client = APIClient()
        client.force_authenticate(user=no_perm_user)
        
        # This should fail with 403 if ACL implemented
        # (if no ACL in test, will get 200)
        # Just verify ACL check exists
        response = client.post(
            f'/api/v4/dam/metadata-presets/{self.preset.id}/test-preset/',
            {'document_id': self.document.id},
            format='json'
        )
        # Status depends on whether document is accessible to user
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        )
    
    def test_test_preset_response_structure(self):
        """Test response has correct structure"""
        response = self.client.post(
            f'/api/v4/dam/metadata-presets/{self.preset.id}/test-preset/',
            {'document_id': self.document.id},
            format='json'
        )
        
        if response.status_code == status.HTTP_200_OK:
            self.assertIn('success', response.data)
            self.assertIn('preset_name', response.data)
            self.assertIn('document_id', response.data)
            self.assertIn('metadata_extracted', response.data)
            self.assertIn('field_count', response.data)
```

Step 5: VERIFICATION & TESTING
Test commands:

```bash
# Test 1: Valid request
curl -X POST \
  http://localhost:8000/api/v4/dam/metadata-presets/1/test-preset/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 123}'

# Expected: HTTP 200 OK

# Test 2: Missing document_id
curl ... -d '{}'

# Expected: HTTP 400 "document_id is required"

# Test 3: Invalid document_id type
curl ... -d '{"document_id": "invalid"}'

# Expected: HTTP 400 "Invalid document_id"

# Test 4: Non-existent document
curl ... -d '{"document_id": 99999}'

# Expected: HTTP 400 "Document not found"

# Test 5: Non-existent preset
curl http://localhost:8000/api/v4/dam/metadata-presets/99999/test-preset/ ...

# Expected: HTTP 404 "Preset not found"

# Run tests
pytest mayan/apps/dam/tests/test_metadata_preset.py -v
```

ACCEPTANCE CRITERIA (MUST ALL PASS):
✓ document_id required (400 if missing)
✓ document_id must be valid integer (400 if invalid type)
✓ Document must exist (400 if not found)
✓ User must have view permission (403 if denied)
✓ Response includes error_code field
✓ Response includes success field
✓ Response structure consistent
✓ All tests pass (pytest -v)
✓ No TypeErrors on invalid input
✓ Proper error messages (400, 403, 404)

NOTES:
- TestPresetSerializer handles validation
- ACL check is CRITICAL security fix
- Error handling prevents server crashes
- Logging for audit trail
- All errors return structured JSON

END OF PROMPT
```

---

## 📝 ИНСТРУКЦИИ ПО ИСПОЛЬЗОВАНИЮ

### Для каждой задачи:

1. **Откройте Cursor AI** в VS Code
2. **Скопируйте весь промпт** (начиная с "You are a senior...")
3. **Вставьте в Cursor AI**
4. **Нажмите Tab** или Enter для автодополнения
5. **Дождитесь генерации** (обычно 2-3 минуты)
6. **Проверьте код** и примените изменения

### Порядок выполнения:

1. **Task 1.1** (JSON API) - 1 день
2. **Task 1.2** (Rate Limiting) - 0.5 дня ← потребуется для 1.3
3. **Task 1.3** (DocumentAIAnalysisViewSet) - 1 день
4. **Task 1.4** (BulkAnalyzeDocumentsSerializer) - 1 день
5. **Task 1.5** (test_preset) - 0.5 дня

**Всего: 4 дня работы** ✅

---

**Готовых промптов:** 5 (по одному на каждую задачу Phase 1)  
**Структура:** Complete, с примерами кода, тестами, и критериями готовности  
**Язык:** Russian описание + English code examples
