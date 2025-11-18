"""
Production settings for Mayan EDMS
This file should be used for production deployments
"""

from . import *  # NOQA

# Security settings for production
DEBUG = False
TEMPLATE_DEBUG = False

# Use environment variable for ALLOWED_HOSTS or default to localhost
import os
ALLOWED_HOSTS = os.environ.get('MAYAN_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/lib/mayan/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Performance optimizations
CELERY_TASK_ALWAYS_EAGER = False

# Database connection pooling for production
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['OPTIONS'] = {
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
}

# Cache settings for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Email backend (configure for production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('MAYAN_EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('MAYAN_EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('MAYAN_EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('MAYAN_EMAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('MAYAN_DEFAULT_FROM_EMAIL', 'noreply@mayan.local')

# File upload limits for production
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Rate limiting (basic implementation)
MIDDLEWARE += [
    'django_ratelimit.middleware.RatelimitMiddleware',
]

# RATELIMIT_VIEW = 'mayan.apps.common.views.limited_view'