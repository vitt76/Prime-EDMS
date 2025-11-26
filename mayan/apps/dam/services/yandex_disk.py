import logging
import os
import tempfile
from typing import Dict, Iterable, List, Optional

import requests
from django.core.files import File
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from mayan.apps.cabinets.models import Cabinet
from mayan.apps.documents.models import Document, DocumentType

from ..models import YandexDiskImportRecord

logger = logging.getLogger(__name__)


class YandexDiskClientError(Exception):
    """Raised when Yandex Disk API returns an error."""


class YandexDiskOAuthError(Exception):
    """Raised when OAuth exchange fails."""


class YandexDiskClient:
    base_url = 'https://cloud-api.yandex.net/v1/disk'

    def __init__(self, token: str, timeout: int = 30):
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'OAuth {token}',
            'Accept': 'application/json'
        })
        self.timeout = timeout

    def ping(self) -> Dict:
        response = self.session.get(
            url=self.base_url, timeout=self.timeout
        )
        self._raise_for_status(response)
        return response.json()

    def list_directory(self, path: str) -> List[Dict]:
        """
        Return flat list of items inside Yandex Disk path.
        """
        params = {
            'path': path,
            'limit': 1000,
            'fields': '_embedded.items.name,_embedded.items.type,_embedded.items.path,_embedded.items.size'
        }
        url = f'{self.base_url}/resources'
        items: List[Dict] = []

        while url:
            response = self.session.get(
                url=url, params=params, timeout=self.timeout
            )
            self._raise_for_status(response)
            payload = response.json()
            embedded = payload.get('_embedded', {})
            items.extend(embedded.get('items', []))
            next_href = embedded.get('next')
            if next_href:
                url = next_href
                params = None
            else:
                url = None

        return items

    def iter_file(self, path: str, chunk_size: int = 1024 * 1024) -> Iterable[bytes]:
        download_meta = self.session.get(
            url=f'{self.base_url}/resources/download',
            params={'path': path},
            timeout=self.timeout
        )
        self._raise_for_status(download_meta)
        href = download_meta.json().get('href')
        if not href:
            raise YandexDiskClientError(_('Download URL missing for %s') % path)

        with self.session.get(href, stream=True, timeout=self.timeout) as response:
            self._raise_for_status(response)
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    yield chunk

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error('Yandex Disk API error: %s - %s', response.url, response.text)
            raise YandexDiskClientError(str(exc)) from exc


class YandexDiskImporter:
    """
    Mirror Yandex Disk folders into Cabinets and Documents.
    """

    def __init__(
        self,
        client: YandexDiskClient,
        document_type: DocumentType,
        base_path: str,
        cabinet_root_label: str,
        max_file_size: int,
        file_limit: int = 0
    ):
        self.client = client
        self.document_type = document_type
        self.base_path = base_path.rstrip('/') or 'disk:/'
        self.cabinet_root_label = cabinet_root_label
        self.max_file_size = max_file_size
        self.file_limit = file_limit
        self.documents_created = 0

    def run(self) -> int:
        logger.info('Starting Yandex Disk import for base path: %s', self.base_path)
        root_cabinet, _ = Cabinet.objects.get_or_create(
            parent=None,
            label=self.cabinet_root_label
        )
        self._import_directory(self.base_path, root_cabinet)
        logger.info('Yandex Disk import completed. Documents created: %s', self.documents_created)
        return self.documents_created

    def _import_directory(self, path: str, parent_cabinet: Cabinet) -> None:
        try:
            items = self.client.list_directory(path=path)
        except YandexDiskClientError as exc:
            logger.error('Failed to list directory %s: %s', path, exc)
            return

        for item in items:
            if self.file_limit and self.documents_created >= self.file_limit:
                logger.info('File limit reached (%s). Stopping import.', self.file_limit)
                return

            item_type = item.get('type')
            item_name = item.get('name') or 'Unnamed'
            item_path = item.get('path')

            if item_type == 'dir':
                child_cabinet, _ = Cabinet.objects.get_or_create(
                    parent=parent_cabinet,
                    label=item_name
                )
                self._import_directory(item_path, child_cabinet)
            elif item_type == 'file':
                self._import_file(item=item, cabinet=parent_cabinet)

    def _import_file(self, item: Dict, cabinet: Cabinet) -> None:
        size = int(item.get('size') or 0)
        if self.max_file_size and size > self.max_file_size:
            logger.warning(
                'Skipping %s (%s bytes) due to size limit %s bytes',
                item.get('path'), size, self.max_file_size
            )
            return

        path = item.get('path')
        if not path:
            return

        if YandexDiskImportRecord.objects.filter(path=path).exists():
            logger.debug('Skipping already imported file: %s', path)
            return

        label = item.get('name') or os.path.basename(path)

        with transaction.atomic():
            document = Document.objects.create(
                document_type=self.document_type,
                label=label
            )
            temp_file_path = None

            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file_path = temp_file.name
                    for chunk in self.client.iter_file(path=path):
                        temp_file.write(chunk)

                with open(temp_file_path, 'rb') as imported_file:
                    document.file_new(
                        file_object=File(imported_file),
                        filename=label
                    )
                cabinet.document_add(document)
                YandexDiskImportRecord.objects.create(
                    path=path,
                    document=document,
                    cabinet=cabinet
                )
                self.documents_created += 1
                logger.info('Imported Yandex Disk file %s into document %s', path, document.pk)
            except Exception as exc:
                logger.error('Failed to import %s: %s', path, exc)
                document.delete()
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)


def exchange_yandex_code_for_token(*, client_id: str, client_secret: str, code: str) -> Dict:
    """
    Exchange one-time verification code for an OAuth token.
    """
    endpoint = 'https://oauth.yandex.ru/token'
    try:
        response = requests.post(
            url=endpoint,
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret
            },
            timeout=30
        )
    except requests.RequestException as exc:
        raise YandexDiskOAuthError(
            _('Failed to reach Yandex OAuth endpoint: %s') % exc
        ) from exc

    if response.status_code >= 400:
        try:
            payload = response.json()
            error_description = payload.get('error_description') or payload.get('error')
        except ValueError:
            error_description = response.text
        raise YandexDiskOAuthError(
            _('OAuth exchange failed: %s') % (error_description or response.status_code)
        )

    try:
        return response.json()
    except ValueError as exc:
        raise YandexDiskOAuthError(_('Invalid JSON in OAuth response.')) from exc

