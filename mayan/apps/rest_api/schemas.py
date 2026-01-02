"""OpenAPI configuration module.

Historically this project used `drf-yasg` and kept OpenAPI metadata here.
The production-ready analytics rollout migrates the project to `drf-spectacular`.

This module is kept to avoid import errors in older references, but it no longer
exports `drf-yasg` objects.
"""

openapi_info = None
