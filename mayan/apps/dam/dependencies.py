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

# Note: requests is already included in Mayan EDMS core dependencies
# so we don't need to declare it here

# All dependencies
dependencies = [
    openai_dependency,
]
