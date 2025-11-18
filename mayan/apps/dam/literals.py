"""
Literals for DAM module.
"""

# Default AI providers priority order
DEFAULT_AI_PROVIDER_PRIORITY = [
    'openai',      # Best for vision and detailed analysis
    'yandexgpt',   # Good for Russian language tasks
    'gigachat',    # Sber's model, good for Russian content
    'claude',      # TODO: Implement
    'gemini',      # TODO: Implement
]

# AI analysis timeouts (in seconds)
AI_ANALYSIS_TIMEOUTS = {
    'openai': 120,      # 2 minutes
    'yandexgpt': 60,    # 1 minute
    'gigachat': 90,     # 1.5 minutes
    'claude': 120,      # 2 minutes
    'gemini': 120,      # 2 minutes
}

# Maximum number of retries for AI analysis
AI_ANALYSIS_MAX_RETRIES = 3

# Delay between retries (in seconds)
AI_ANALYSIS_RETRY_DELAY = 60

# Supported image MIME types for AI analysis
SUPPORTED_IMAGE_TYPES = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/tiff',
    'image/bmp',
    'image/svg+xml',
]

# Maximum file size for AI analysis (in bytes)
MAX_AI_ANALYSIS_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Default metadata preset
DEFAULT_METADATA_PRESET = {
    'name': 'Default AI Analysis',
    'description': 'Standard AI analysis for images',
    'ai_providers': {
        'openai': {'priority': 1, 'enabled': True},
        'yandexgpt': {'priority': 2, 'enabled': True},
        'gigachat': {'priority': 3, 'enabled': True},
    },
    'extract_description': True,
    'extract_tags': True,
    'extract_colors': True,
    'extract_alt_text': True,
    'supported_mime_types': SUPPORTED_IMAGE_TYPES,
    'is_enabled': True,
}
