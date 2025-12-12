"""
WSGI config for mayan project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')

# #region agent log
try:
    log_line = {
        "id": "log_wsgi_start",
        "timestamp": __import__("time").time() * 1000,
        "sessionId": "debug-session",
        "runId": "pre-fix",
        "hypothesisId": "H1",
        "location": "mayan/wsgi.py:top",
        "message": "WSGI init start",
        "data": {}
    }
    with open(r"c:\DAM\Prime-EDMS\.cursor\debug.log", "a", encoding="utf-8") as _f:
        import json as _json
        _f.write(_json.dumps(log_line) + "\n")
except Exception:
    pass
# #endregion agent log

# #region agent log http
try:
    import json as _json
    import urllib.request as _r
    _r.urlopen(
        _r.Request(
            "http://host.docker.internal:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac",
            data=_json.dumps({
                "id": "log_wsgi_start_http",
                "timestamp": __import__("time").time() * 1000,
                "sessionId": "debug-session",
                "runId": "pre-fix",
                "hypothesisId": "H1",
                "location": "mayan/wsgi.py:top",
                "message": "WSGI init start",
                "data": {}
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        ),
        timeout=2
    )
except Exception:
    pass
# #endregion agent log

application = get_wsgi_application()

# #region agent log
try:
    log_line = {
        "id": "log_wsgi_ready",
        "timestamp": __import__("time").time() * 1000,
        "sessionId": "debug-session",
        "runId": "pre-fix",
        "hypothesisId": "H1",
        "location": "mayan/wsgi.py:after",
        "message": "WSGI init completed",
        "data": {}
    }
    with open(r"c:\DAM\Prime-EDMS\.cursor\debug.log", "a", encoding="utf-8") as _f:
        import json as _json
        _f.write(_json.dumps(log_line) + "\n")
except Exception:
    pass
# #endregion agent log

# #region agent log http
try:
    import json as _json
    import urllib.request as _r
    _r.urlopen(
        _r.Request(
            "http://host.docker.internal:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac",
            data=_json.dumps({
                "id": "log_wsgi_ready_http",
                "timestamp": __import__("time").time() * 1000,
                "sessionId": "debug-session",
                "runId": "pre-fix",
                "hypothesisId": "H1",
                "location": "mayan/wsgi.py:after",
                "message": "WSGI init completed",
                "data": {}
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        ),
        timeout=2
    )
except Exception:
    pass
# #endregion agent log
