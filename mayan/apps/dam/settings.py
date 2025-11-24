from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

namespace = SettingNamespace(
    label=_('Digital Asset Management'), name='dam', version='0001'
)

# Общие настройки AI-анализа
setting_ai_analysis_enabled = namespace.add_setting(
    default=True,
    global_name='DAM_AI_ANALYSIS_ENABLED',
    help_text=_(
        'Enable automatic AI analysis for uploaded documents. '
        'When enabled, new documents will be automatically analyzed using configured AI providers.'
    )
)

setting_ai_analysis_auto_trigger = namespace.add_setting(
    default=True,
    global_name='DAM_AI_ANALYSIS_AUTO_TRIGGER',
    help_text=_(
        'Automatically trigger AI analysis when new documents are uploaded. '
        'Disable to require manual analysis initiation.'
    )
)

setting_ai_analysis_timeout = namespace.add_setting(
    default=120,
    global_name='DAM_AI_ANALYSIS_TIMEOUT',
    help_text=_(
        'Maximum time in seconds to wait for AI analysis completion. '
        'Increase for slower AI providers or complex documents.'
    )
)

setting_ai_analysis_max_retries = namespace.add_setting(
    default=3,
    global_name='DAM_AI_ANALYSIS_MAX_RETRIES',
    help_text=_(
        'Maximum number of retries for failed AI analysis attempts. '
        'Set to 0 to disable retries.'
    )
)

setting_ai_analysis_retry_delay = namespace.add_setting(
    default=300,
    global_name='DAM_AI_ANALYSIS_RETRY_DELAY',
    help_text=_(
        'Delay in seconds between AI analysis retry attempts.'
    )
)

# Настройки провайдеров
setting_ai_providers_active = namespace.add_setting(
    default=['gigachat', 'openai', 'claude', 'gemini', 'yandexgpt', 'kieai'],
    global_name='DAM_AI_PROVIDERS_ACTIVE',
    help_text=_(
        'List of active AI providers. Only providers in this list will be used for analysis. '
        'Available providers: gigachat, openai, claude, gemini, yandexgpt, kieai'
    )
)

setting_ai_provider_fallback = namespace.add_setting(
    default=True,
    global_name='DAM_AI_PROVIDER_FALLBACK',
    help_text=_(
        'Enable fallback to alternative providers when primary provider fails. '
        'If disabled, analysis will fail if primary provider is unavailable.'
    )
)

# Настройки GigaChat
setting_gigachat_credentials = namespace.add_setting(
    default='',
    global_name='DAM_GIGACHAT_CREDENTIALS',
    help_text=_(
        'GigaChat API credentials. Format: client_id:client_secret'
    )
)

setting_gigachat_scope = namespace.add_setting(
    default='GIGACHAT_API_PERS',
    global_name='DAM_GIGACHAT_SCOPE',
    help_text=_(
        'GigaChat API scope. Default: GIGACHAT_API_PERS'
    )
)

setting_gigachat_verify_ssl = namespace.add_setting(
    default=False,
    global_name='DAM_GIGACHAT_VERIFY_SSL_CERTS',
    help_text=_(
        'Verify SSL certificates for GigaChat API calls. '
        'Disable only if you trust the connection.'
    )
)

setting_gigachat_model = namespace.add_setting(
    default='GigaChat',
    global_name='DAM_GIGACHAT_MODEL',
    help_text=_(
        'GigaChat model to use. Default: GigaChat'
    )
)

# Настройки OpenAI
setting_openai_api_key = namespace.add_setting(
    default='',
    global_name='DAM_OPENAI_API_KEY',
    help_text=_(
        'OpenAI API key for GPT models.'
    )
)

setting_openai_model = namespace.add_setting(
    default='gpt-4',
    global_name='DAM_OPENAI_MODEL',
    help_text=_(
        'OpenAI model to use. Options: gpt-4, gpt-3.5-turbo'
    )
)

setting_openai_max_tokens = namespace.add_setting(
    default=2000,
    global_name='DAM_OPENAI_MAX_TOKENS',
    help_text=_(
        'Maximum tokens for OpenAI API responses.'
    )
)

# Настройки Claude
setting_claude_api_key = namespace.add_setting(
    default='',
    global_name='DAM_CLAUDE_API_KEY',
    help_text=_(
        'Anthropic Claude API key.'
    )
)

setting_claude_model = namespace.add_setting(
    default='claude-3-sonnet-20240229',
    global_name='DAM_CLAUDE_MODEL',
    help_text=_(
        'Claude model to use. Options: claude-3-sonnet-20240229, claude-3-haiku-20240307'
    )
)

setting_claude_max_tokens = namespace.add_setting(
    default=2000,
    global_name='DAM_CLAUDE_MAX_TOKENS',
    help_text=_(
        'Maximum tokens for Claude API responses.'
    )
)

# Настройки Gemini
setting_gemini_api_key = namespace.add_setting(
    default='',
    global_name='DAM_GEMINI_API_KEY',
    help_text=_(
        'Google Gemini API key.'
    )
)

setting_gemini_model = namespace.add_setting(
    default='gemini-pro',
    global_name='DAM_GEMINI_MODEL',
    help_text=_(
        'Gemini model to use. Options: gemini-pro, gemini-pro-vision'
    )
)

setting_gemini_max_tokens = namespace.add_setting(
    default=2000,
    global_name='DAM_GEMINI_MAX_TOKENS',
    help_text=_(
        'Maximum tokens for Gemini API responses.'
    )
)

# Настройки YandexGPT
setting_yandexgpt_api_key = namespace.add_setting(
    default='',
    global_name='DAM_YANDEXGPT_API_KEY',
    help_text=_(
        'YandexGPT API key.'
    )
)

setting_yandexgpt_iam_token = namespace.add_setting(
    default='',
    global_name='DAM_YANDEXGPT_IAM_TOKEN',
    help_text=_(
        'YandexGPT IAM token (alternative to API key).'
    )
)

setting_yandexgpt_folder_id = namespace.add_setting(
    default='',
    global_name='DAM_YANDEXGPT_FOLDER_ID',
    help_text=_(
        'YandexGPT folder ID for API calls.'
    )
)

setting_yandexgpt_model = namespace.add_setting(
    default='yandexgpt-lite',
    global_name='DAM_YANDEXGPT_MODEL',
    help_text=_(
        'YandexGPT model to use. Options: yandexgpt-lite, yandexgpt'
    )
)

# Настройки Kie.ai
setting_kieai_api_key = namespace.add_setting(
    default='',
    global_name='DAM_KIEAI_API_KEY',
    help_text=_(
        'Kie.ai API key (Bearer token). Получается в личном кабинете Kie.ai.'
    )
)

setting_kieai_base_url = namespace.add_setting(
    default='https://api.kie.ai/api/v1/flux/kontext',
    global_name='DAM_KIEAI_BASE_URL',
    help_text=_(
        'Базовый URL Flux Kontext API (например, https://api.kie.ai/api/v1/flux/kontext).'
    )
)

setting_kieai_upload_url = namespace.add_setting(
    default='https://kieai.redpandaai.co/api/file-stream-upload',
    global_name='DAM_KIEAI_UPLOAD_URL',
    help_text=_(
        'Полный URL upload-эндпоинта Kie.ai (`POST /api/file-stream-upload`). '
        'Используется для стриминга файлов в Cloudflare R2.'
    )
)

setting_kieai_ocr_endpoint = namespace.add_setting(
    default='generate',
    global_name='DAM_KIEAI_OCR_ENDPOINT',
    help_text=_(
        'Endpoint Flux Kontext для запуска задачи (по умолчанию `POST /generate`).'
    )
)

setting_kieai_status_endpoint = namespace.add_setting(
    default='record-info',
    global_name='DAM_KIEAI_STATUS_ENDPOINT',
    help_text=_(
        'Endpoint Flux Kontext для получения статуса (`GET /record-info?taskId=...`).'
    )
)

setting_kieai_upload_path = namespace.add_setting(
    default='prime-edms/dam',
    global_name='DAM_KIEAI_UPLOAD_PATH',
    help_text=_(
        'Каталог в Kie.ai R2, куда будут загружаться изображения для анализа.'
    )
)

setting_kieai_default_language = namespace.add_setting(
    default='ru',
    global_name='DAM_KIEAI_DEFAULT_LANGUAGE',
    help_text=_(
        'Язык, в котором требуется получить расшифровку (ISO/BCP-47).'
    )
)

setting_kieai_timeout = namespace.add_setting(
    default=45,
    global_name='DAM_KIEAI_TIMEOUT',
    help_text=_(
        'Таймаут HTTP-запросов к Kie.ai в секундах.'
    )
)

# Настройки анализа документов
setting_analysis_text_max_length = namespace.add_setting(
    default=10000,
    global_name='DAM_ANALYSIS_TEXT_MAX_LENGTH',
    help_text=_(
        'Maximum text length to analyze for document content. '
        'Longer documents will be truncated.'
    )
)

setting_analysis_image_max_size = namespace.add_setting(
    default=10 * 1024 * 1024,  # 10MB
    global_name='DAM_ANALYSIS_IMAGE_MAX_SIZE',
    help_text=_(
        'Maximum image file size in bytes for AI analysis. '
        'Larger images will be skipped.'
    )
)

setting_analysis_metadata_format = namespace.add_setting(
    default='json',
    global_name='DAM_ANALYSIS_METADATA_FORMAT',
    help_text=_(
        'Format for storing AI analysis metadata. Options: json, yaml'
    )
)

# Настройки производительности
setting_analysis_queue = namespace.add_setting(
    default='documents',
    global_name='DAM_ANALYSIS_QUEUE',
    help_text=_(
        'Celery queue name for AI analysis tasks.'
    )
)

setting_analysis_priority = namespace.add_setting(
    default=5,
    global_name='DAM_ANALYSIS_PRIORITY',
    help_text=_(
        'Priority for AI analysis tasks (1-10, higher = more priority).'
    )
)

setting_analysis_concurrent_limit = namespace.add_setting(
    default=2,
    global_name='DAM_ANALYSIS_CONCURRENT_LIMIT',
    help_text=_(
        'Maximum number of concurrent AI analysis tasks per worker.'
    )
)

# Настройки логирования
setting_logging_level = namespace.add_setting(
    default='INFO',
    global_name='DAM_LOGGING_LEVEL',
    help_text=_(
        'Logging level for DAM operations. Options: DEBUG, INFO, WARNING, ERROR'
    )
)

setting_logging_save_responses = namespace.add_setting(
    default=False,
    global_name='DAM_LOGGING_SAVE_RESPONSES',
    help_text=_(
        'Save AI provider API responses to log files for debugging. '
        'Enable only for troubleshooting.'
    )
)
