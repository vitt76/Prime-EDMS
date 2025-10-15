import logging
from pathlib import Path
import re

from django.core.files import File
from django.utils.translation import ugettext_lazy as _

from mayan.apps.storage.models import SharedUploadedFile

from ..classes import SourceBackend
from ..exceptions import SourceException

from .literals import (
    REGULAR_EXPRESSION_MATCH_EVERYTHING, REGULAR_EXPRESSION_MATCH_NOTHING,
    SOURCE_INTERVAL_UNCOMPRESS_CHOICES
)
from .mixins import (
    SourceBackendCompressedMixin, SourceBackendPeriodicMixin, SourceBaseMixin
)

__all__ = ('SourceBackendWatchFolder',)
logger = logging.getLogger(name=__name__)


class SourceBackendWatchFolder(
    SourceBackendCompressedMixin, SourceBackendPeriodicMixin,
    SourceBaseMixin, SourceBackend
):
    field_order = (
        'folder_path', 'include_subdirectories', 'include_regex',
        'exclude_regex'
    )
    fields = {
        'folder_path': {
            'class': 'django.forms.CharField',
            'default': '',
            'help_text': _(
                'Server side filesystem path.'
            ),
            'kwargs': {
                'max_length': 255,
            },
            'label': _('Folder path'),
            'required': True
        },
        'include_subdirectories': {
            'class': 'django.forms.BooleanField',
            'default': '',
            'help_text': _(
                'If checked, not only will the folder path be scanned for '
                'files but also its subdirectories.'
            ),
            'label': _('Include subdirectories?'),
            'required': False
        },
        'include_regex': {
            'class': 'django.forms.CharField',
            'default': '',
            'help_text': _(
                'Regular expression used to select which files to upload.'
            ),
            'label': _('Include regular expression'),
            'required': False
        },
        'exclude_regex': {
            'class': 'django.forms.CharField',
            'default': '',
            'help_text': _(
                'Regular expression used to exclude which files to upload.'
            ),
            'label': _('Exclude regular expression'),
            'required': False
        }
    }
    label = _('Watch folder')
    uncompress_choices = SOURCE_INTERVAL_UNCOMPRESS_CHOICES

    def get_shared_uploaded_files(self):
        dry_run = self.process_kwargs.get('dry_run', False)
        include_regex = re.compile(
            pattern=self.kwargs.get(
                'include_regex', REGULAR_EXPRESSION_MATCH_EVERYTHING
            )
        )
        exclude_regex = re.compile(
            pattern=self.kwargs.get(
                'exclude_regex', REGULAR_EXPRESSION_MATCH_NOTHING
            ) or REGULAR_EXPRESSION_MATCH_NOTHING
        )
        path = Path(self.kwargs['folder_path'])

        # Force testing the path and raise errors for the log.
        path.lstat()
        if not path.is_dir():
            raise SourceException('Path {} is not a directory.'.format(path))

        if self.kwargs.get('include_subdirectories', False):
            iterator = path.rglob(pattern='*')
        else:
            iterator = path.glob(pattern='*')

        for entry in iterator:
            if entry.is_file() or entry.is_symlink():
                if include_regex.match(string=entry.name) and not exclude_regex.match(string=entry.name):
                    with entry.open(mode='rb+') as file_object:
                        shared_uploaded_file = SharedUploadedFile.objects.create(
                            file=File(file=file_object), filename=entry.name
                        )
                        if not dry_run:
                            entry.unlink()

                        return (shared_uploaded_file,)
