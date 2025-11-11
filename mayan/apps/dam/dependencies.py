"""
Dependencies for DAM module.

Lists external packages required for AI providers.
"""

from mayan.apps.dependencies.classes import PythonDependency

# Optional dependencies for specific providers
openai_dependency = PythonDependency(
    module='openai',
    name='openai',
    version_string='>=1.0.0',
    help_text='Required for OpenAI Vision API integration.'
)

# AI Provider dependencies
gigachat_dependency = PythonDependency(
    module='gigachat',
    name='gigachat',
    help_text='Official GigaChat Python library by ai-forever.'
)

yandexgptlite_dependency = PythonDependency(
    module='yandexgptlite',
    name='yandexgptlite',
    help_text='Lightweight YandexGPT integration library.'
)

# YandexGPT authorized key dependencies (fallback)
cryptography_dependency = PythonDependency(
    module='cryptography',
    name='cryptography',
    version_string='>=3.4.0',
    help_text='Required for YandexGPT authorized key authentication.'
)

pyjwt_dependency = PythonDependency(
    module='jwt',
    name='PyJWT',
    version_string='>=2.0.0',
    help_text='Required for JWT token creation in YandexGPT authentication.'
)

# Note: requests is already included in Mayan EDMS core dependencies
# so we don't need to declare it here

# All dependencies
dependencies = [
    openai_dependency,
    gigachat_dependency,
    yandexgptlite_dependency,
    cryptography_dependency,
    pyjwt_dependency,
]
