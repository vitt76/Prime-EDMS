import os
import sys

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.utils import SettingNamespaceSingleton

from .literals import DEFAULT_SECRET_KEY, SECRET_KEY_FILENAME, SYSTEM_DIR

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

setting_namespace = SettingNamespaceSingleton(global_symbol_table=globals())
if 'revertsettings' in sys.argv:
    setting_namespace.update_globals(only_critical=True)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(MEDIA_ROOT, 'db.sqlite3')  # NOQA: F821
        }
    }
else:
    setting_namespace.update_globals()

environment_secret_key = os.environ.get('MAYAN_SECRET_KEY')
if environment_secret_key:
    SECRET_KEY = environment_secret_key
else:
    SECRET_KEY_PATH = os.path.join(MEDIA_ROOT, SYSTEM_DIR, SECRET_KEY_FILENAME)
    try:
        with open(file=SECRET_KEY_PATH) as file_object:  # NOQA: F821
            SECRET_KEY = file_object.read().strip()
    except IOError:
        SECRET_KEY = DEFAULT_SECRET_KEY

# Application definition

INSTALLED_APPS = (
    # Placed at the top so it can preload all events defined by apps.
    'mayan.apps.events',
    # Placed at the top so it can override any template.
    'mayan.apps.appearance',
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.forms',
    'django.contrib.staticfiles',
    # 3rd party.
    'actstream',
    'corsheaders',
    'django_celery_beat',
    'formtools',
    'mathfilters',
    'mptt',
    'rest_framework',
    'rest_framework.authtoken',
    'solo',
    'stronghold',
    'widget_tweaks',
    # Base apps
    # Moved to the top to ensure Mayan app logging is initialized and
    # available as soon as possible.
    'mayan.apps.logging',
    # Task manager goes to the top to ensure all queues are created before any
    # other app tries to use them.
    'mayan.apps.task_manager',
    'mayan.apps.acls',
    # User management app must go before authentication to ensure the Group
    # and User models are properly setup using runtime methods.
    'mayan.apps.user_management',
    'mayan.apps.authentication',
    'mayan.apps.authentication_otp',
    'mayan.apps.autoadmin',
    'mayan.apps.common',
    'mayan.apps.converter',
    'mayan.apps.dashboards',
    'mayan.apps.databases',
    'mayan.apps.dependencies',
    'mayan.apps.django_gpg',
    'mayan.apps.dynamic_search',
    'mayan.apps.file_caching',
    'mayan.apps.locales',
    'mayan.apps.lock_manager',
    'mayan.apps.messaging',
    'mayan.apps.mime_types',
    'mayan.apps.navigation',
    'mayan.apps.organizations',
    'mayan.apps.permissions',
    'mayan.apps.platform',
    'mayan.apps.quotas',
    'mayan.apps.rest_api',
    'mayan.apps.headless_api',  # SPA-friendly API endpoints
    'mayan.apps.smart_settings',
    'mayan.apps.storage',
    'mayan.apps.templating',
    'mayan.apps.testing',
    'mayan.apps.views',
    # Obsolete apps. Need to remain to allow migrations to execute.
    'mayan.apps.announcements',
    'mayan.apps.motd',
    # Document apps.
    'mayan.apps.cabinets',
    'mayan.apps.checkouts',
    'mayan.apps.document_comments',
    'mayan.apps.document_indexing',
    'mayan.apps.document_parsing',
    'mayan.apps.document_signatures',
    'mayan.apps.document_states',
    'mayan.apps.documents',
    'mayan.apps.duplicates',
    'mayan.apps.file_metadata',
    'mayan.apps.linking',
    'mayan.apps.mailer',
    'mayan.apps.mayan_statistics',
    'mayan.apps.metadata',
    'mayan.apps.mirroring',
    'mayan.apps.ocr',
    'mayan.apps.redactions',
    'mayan.apps.signature_captures',
    'mayan.apps.sources',
    'mayan.apps.tags',
    'mayan.apps.web_links',
    # Placed after rest_api to allow template overriding.
    'drf_yasg'
)

MIDDLEWARE = (
    'mayan.apps.logging.middleware.error_logging.ErrorLoggingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mayan.apps.locales.middleware.locales.UserLocaleProfileMiddleware',
    'mayan.apps.authentication.middleware.impersonate.ImpersonateMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'stronghold.middleware.LoginRequiredMiddleware',
    'mayan.apps.views.middleware.ajax_redirect.AjaxRedirect'
)

ROOT_URLCONF = 'mayan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ]
        }
    }
]

WSGI_APPLICATION = 'mayan.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    }
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# ------------ Custom settings section ----------

LANGUAGES = (
    ('ar', _('Arabic')),
    ('bg', _('Bulgarian')),
    ('bs', _('Bosnian')),
    ('cs', _('Czech')),
    ('da', _('Danish')),
    ('de', _('German')),
    ('el', _('Greek')),
    ('en', _('English')),
    ('es', _('Spanish')),
    ('es-pr', _('Spanish (Puerto Rico)')),
    ('fa', _('Persian')),
    ('fr', _('French')),
    ('hu', _('Hungarian')),
    ('id', _('Indonesian')),
    ('it', _('Italian')),
    ('lv', _('Latvian')),
    ('nl', _('Dutch')),
    ('pl', _('Polish')),
    ('pt', _('Portuguese')),
    ('pt-br', _('Portuguese (Brazil)')),
    ('ro', _('Romanian')),
    ('ru', _('Russian')),
    ('sl', _('Slovenian')),
    ('tr', _('Turkish')),
    ('vi', _('Vietnamese')),
    ('zh-hans', _('Chinese (Simplified)'))
)

# Path to locale files
LOCALE_PATHS = [
    '/opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/documents/locale',
]

MEDIA_URL = 'media/'

SITE_ID = 1

STATIC_ROOT = os.environ.get(
    'MAYAN_STATIC_ROOT', os.path.join(MEDIA_ROOT, 'static')  # NOQA: F821
)

MEDIA_URL = 'media/'

# Silence warning and keep default for the time being.
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'mayan.apps.views.finders.MayanAppDirectoriesFinder'
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

TEST_RUNNER = 'mayan.apps.testing.runner.MayanTestRunner'

# ---------- Django REST framework -----------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'mayan.apps.rest_api.pagination.MayanPageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'ai_analysis': '10/minute,50/hour,500/day',
        'ai_analysis_anon': '1/hour',
        'upload': '50/hour',
        'download': '100/hour',
        'bulk_operation': '20/hour',
    },
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    # Use default DRF exception handler
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

REST_FRAMEWORK_EXTENDED = {
    'SHOW_THROTTLE_HEADERS': True,
}

# Caching configuration (used for throttling counters)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mayan-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'api_errors': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'throttle_log': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        # 'ai_analysis': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': 'logs/ai_analysis.log',
        #     'maxBytes': 1024 * 1024 * 10,
        #     'backupCount': 10,
        #     'formatter': 'json',
        # },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['api_errors'],
            'level': 'ERROR',
            'propagate': False,
        },
        'rest_framework': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'mayan.apps.dam': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'dam.throttle': {
            'handlers': ['throttle_log'],
            'level': 'WARNING',
            'propagate': False,
        },
        'mayan.apps.dam.throttle': {
            'handlers': ['throttle_log'],
            'level': 'WARNING',
            'propagate': False,
        },
    }
}

# Security and CSRF for API clients
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'https://yourdomain.com',
]

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'DEFAULT_SRC': ('"self"',),
    'SCRIPT_SRC': ('"self"', 'https://cdn.jsdelivr.net'),
    'STYLE_SRC': ('"self"', 'https://fonts.googleapis.com'),
    'FONT_SRC': ('"self"', 'https://fonts.gstatic.com'),
    'CONNECT_SRC': ('"self"', 'https://api.example.com'),
}

# --------- Pagination --------

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 5,
    'MARGIN_PAGES_DISPLAYED': 2
}

# ----------- Celery ----------

CELERY_ACCEPT_CONTENT = ('json',)
CELERY_BEAT_SCHEDULE = {}
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ENABLE_UTC = True
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_CREATE_MISSING_QUEUES = True
CELERY_TASK_DEFAULT_QUEUE = 'celery'
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_QUEUES = []
CELERY_TASK_ROUTES = {}
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# ------------ CORS ------------

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'https://yourdomain.com',
]

CORS_ALLOW_CREDENTIALS = True

# ------ Timezone --------

TIMEZONE_COOKIE_NAME = 'django_timezone'
TIMEZONE_SESSION_KEY = 'django_timezone'

# ----- Stronghold -------

STRONGHOLD_PUBLIC_URLS = (
    r'^/favicon\.ico$',
    r'^/converter-pipeline/document-files/\d+/convert/$',
    r'^/publish/.*$',
)

# ----- Swagger --------

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'rest_api.schemas.openapi_info',
    'DEFAULT_MODEL_DEPTH': 1,
    'DOC_EXPANSION': 'None'
}

# ----- Distribution -------

DISTRIBUTION_RENDITION_PRESETS = [
    {
        'resource_type': 'image',
        'format': 'jpeg',
        'width': 1920,
        'height': 1080,
        'quality': 85,
        'watermark': {}
    },
    {
        'resource_type': 'image',
        'format': 'png',
        'width': 800,
        'height': None,
        'quality': None,
        'watermark': {}
    },
    {
        'resource_type': 'document',
        'format': 'pdf',
        'width': None,
        'height': None,
        'quality': None,
        'watermark': {}
    }
]

DISTRIBUTION_DEFAULT_EXPIRATION_DAYS = 30
DISTRIBUTION_MAX_DOWNLOADS = 100
DISTRIBUTION_FFMPEG_PATH = '/usr/bin/ffmpeg'
DISTRIBUTION_CONVERT_TIMEOUT = 300  # 5 minutes
DISTRIBUTION_STORAGE = 'local'  # 'local' or 's3'
DISTRIBUTION_WATERMARK_DEFAULTS = {
    'text': 'SAMPLE',
    'font_size': 24,
    'opacity': 0.3,
    'position': 'center'
}

# Search backend - use Django backend for better compatibility with DAM features
# Django backend doesn't require indexing and works directly with database
SEARCH_BACKEND = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'

# ------ End -----

BASE_INSTALLED_APPS = INSTALLED_APPS

for app in INSTALLED_APPS:
    if 'mayan.apps.{}'.format(app) in BASE_INSTALLED_APPS:
        raise ImproperlyConfigured(
            'Update the app references in the file config.yml as detailed '
            'in https://docs.mayan-edms.com/releases/3.2.html#backward-incompatible-changes'
        )

repeated_apps = tuple(
    set(COMMON_EXTRA_APPS_PRE).intersection(set(COMMON_EXTRA_APPS))
)
if repeated_apps:
    raise ImproperlyConfigured(
        'Apps "{}" cannot be specified in `COMMON_EXTRA_APPS_PRE` and '
        '`COMMON_EXTRA_APPS` at the same time.'.format(
            ', '.join(tuple(repeated_apps))
        )
    )

INSTALLED_APPS = tuple(COMMON_EXTRA_APPS_PRE or ()) + INSTALLED_APPS  # NOQA: F821

INSTALLED_APPS = INSTALLED_APPS + tuple(COMMON_EXTRA_APPS or ())  # NOQA: F821

INSTALLED_APPS = [
    APP for APP in INSTALLED_APPS if APP not in (COMMON_DISABLED_APPS or ())  # NOQA: F821
]

if not DATABASES:
    if DATABASE_ENGINE:  # NOQA: F821
        DATABASES = {
            'default': {
                'ENGINE': DATABASE_ENGINE,  # NOQA: F821
                'NAME': DATABASE_NAME,  # NOQA: F821
                'USER': DATABASE_USER,  # NOQA: F821
                'PASSWORD': DATABASE_PASSWORD,  # NOQA: F821
                'HOST': DATABASE_HOST,  # NOQA: F821
                'PORT': DATABASE_PORT,  # NOQA: F821
                'CONN_MAX_AGE': DATABASE_CONN_MAX_AGE  # NOQA: F821
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(MEDIA_ROOT, 'db.sqlite3')  # NOQA: F821
            }
        }
