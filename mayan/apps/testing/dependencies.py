from mayan.apps.dependencies.classes import (
    BinaryDependency, PythonDependency
)
from mayan.apps.dependencies.environments import environment_testing

from .literals import DEFAULT_FIREFOX_GECKODRIVER_PATH

BinaryDependency(
    environment=environment_testing, label='firefox-geckodriver',
    module=__name__, name='geckodriver',
    path=DEFAULT_FIREFOX_GECKODRIVER_PATH
)
PythonDependency(
    environment=environment_testing, module=__name__, name='coverage',
    version_string='==5.5'
)
PythonDependency(
    environment=environment_testing, module=__name__, name='coveralls',
    version_string='==3.2.0'
)
PythonDependency(
    environment=environment_testing, module=__name__,
    name='django-test-migrations', version_string='==1.1.0'
)
PythonDependency(
    environment=environment_testing, module=__name__, name='selenium',
    version_string='==3.141.0'
)
PythonDependency(
    environment=environment_testing, module=__name__, name='tox',
    version_string='==3.24.3'
)
PythonDependency(
    environment=environment_testing, module=__name__, name='psutil',
    version_string='==5.8.0'
)
