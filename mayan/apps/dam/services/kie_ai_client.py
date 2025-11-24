import logging
import os
import time
import uuid
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests


logger = logging.getLogger(__name__)


class KieAIClientError(Exception):
    """Base error for Kie.ai client failures."""


class KieAIClientResponseError(KieAIClientError):
    """Raised when Kie.ai returns an unsuccessful response."""


class KieAIClient:
    """
    Thin wrapper around the public Kie.ai REST APIs that we need:

    1. `POST /api/file-stream-upload` — выгрузка бинарных данных в R2.
    2. OCR endpoint (настраиваемый) — получение текста по URL загруженного файла.
    """

    DEFAULT_UPLOAD_ENDPOINT = 'api/file-stream-upload'

    def __init__(
        self,
        api_key: str,
        base_url: str,
        upload_url: Optional[str] = None,
        ocr_endpoint: str = 'generate',
        status_endpoint: str = 'record-info',
        default_language: str = 'en',
        timeout: int = 30,
        upload_path: str = 'prime-edms/dam',
        model: str = 'flux-kontext-pro',
        default_prompt: str = 'Опиши содержимое изображения максимально подробно.',
        aspect_ratio: str = '1:1',
        session: Optional[requests.Session] = None
    ):
        if not api_key:
            raise KieAIClientError('API key is required for Kie.ai client')

        if not base_url:
            raise KieAIClientError('Base URL is required for Kie.ai client')

        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip('/') + '/'
        self.upload_url = (upload_url or urljoin(self.base_url, self.DEFAULT_UPLOAD_ENDPOINT)).rstrip('/')
        self.ocr_endpoint = ocr_endpoint.strip('/')
        self.status_endpoint = status_endpoint.strip('/')
        self.default_language = default_language or 'en'
        self.timeout = timeout
        self.upload_path = upload_path
        self.session = session or requests.Session()
        self.model = model
        self.default_prompt = default_prompt
        self.aspect_ratio = aspect_ratio

    # ------------------------------------------------------------------ helpers
    def _headers(self, is_json: bool = True) -> Dict[str, str]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        if is_json:
            headers['Content-Type'] = 'application/json'
        return headers

    def _build_url(self, endpoint: str) -> str:
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            return endpoint
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise KieAIClientResponseError(f'Invalid JSON from Kie.ai: {exc}') from exc

        if not response.ok or not payload.get('success', True):
            message = payload.get('msg') or payload.get('message') or response.text
            raise KieAIClientResponseError(
                f'Kie.ai responded with error {response.status_code}: {message}'
            )

        return payload

    # ------------------------------------------------------------------ public API
    def upload_file(
        self,
        file_name: Optional[str],
        file_bytes: bytes,
        upload_path: str = 'prime-edms/dam'
    ) -> Dict[str, Any]:
        """
        Upload file to Kie.ai storage. Returns response `data` dict.
        """
        if not isinstance(file_bytes, (bytes, bytearray)):
            raise KieAIClientError('file_bytes must be raw bytes')

        safe_name = file_name or f'{uuid.uuid4().hex}.bin'
        upload_path = upload_path.strip('/ ')

        file_tuple = (os.path.basename(safe_name), file_bytes)
        files = {
            'file': file_tuple,
            'fileStream': file_tuple
        }
        data = {'uploadPath': upload_path}
        if file_name:
            data['fileName'] = os.path.basename(file_name)

        logger.debug('Uploading file to Kie.ai R2: name=%s path=%s', safe_name, upload_path)

        try:
            response = self.session.post(
                self.upload_url,
                headers=self._headers(is_json=False),
                files=files,
                data=data,
                timeout=self.timeout
            )
        except requests.exceptions.RequestException as exc:
            raise KieAIClientError(f'Network error while uploading to Kie.ai: {exc}') from exc
        except Exception as exc:  # pragma: no cover - safety net
            raise KieAIClientError(f'Unexpected error while uploading to Kie.ai: {exc}') from exc

        payload = self._handle_response(response)
        data = payload.get('data') or {}

        if 'downloadUrl' not in data:
            raise KieAIClientResponseError('Kie.ai upload response missing downloadUrl')

        return data

    def recognize_image(
        self,
        download_url: str,
        target_language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call OCR/vision endpoint. The endpoint is configurable because Kie.ai
        не публикует явного OCR API в открытых доках.
        """
        if not download_url:
            raise KieAIClientError('download_url is required for OCR call')

        job_data = self._start_image_description(
            image_url=download_url,
            target_language=target_language,
            prompt=prompt
        )
        task_id = job_data.get('taskId') or job_data.get('id')
        if not task_id:
            raise KieAIClientResponseError('Kie.ai OCR response missing taskId')

        details = self._poll_image_description(task_id=task_id)
        response_block = details.get('response') or {}
        content = (
            details.get('content')
            or details.get('result')
            or response_block.get('resultText')
            or response_block.get('resultImageUrl')
            or response_block.get('originImageUrl')
            or ''
        )

        return {
            'text': content.strip(),
            'language': details.get('language') or (target_language or self.default_language),
            'confidence': details.get('confidence'),
            'raw': {
                'job': job_data,
                'details': details
            }
        }

    def _start_image_description(
        self,
        image_url: str,
        target_language: Optional[str],
        prompt: Optional[str]
    ) -> Dict[str, Any]:
        payload = {
            'inputImage': image_url,
            'model': self.model,
            'prompt': prompt or self.default_prompt,
            'aspectRatio': self.aspect_ratio
        }
        if target_language:
            payload['targetLanguage'] = target_language

        endpoint_url = self._build_url(self.ocr_endpoint)
        logger.debug('Starting Kie.ai image description job at %s', endpoint_url)

        try:
            response = self.session.post(
                endpoint_url,
                headers=self._headers(),
                json=payload,
                timeout=self.timeout
            )
        except requests.exceptions.RequestException as exc:
            raise KieAIClientError(f'Network error during OCR request: {exc}') from exc
        except Exception as exc:  # pragma: no cover
            raise KieAIClientError(f'Unexpected error during OCR request: {exc}') from exc

        return self._handle_response(response).get('data') or {}

    def _poll_image_description(self, task_id: str, max_attempts: int = 15, delay: int = 2) -> Dict[str, Any]:
        for attempt in range(1, max_attempts + 1):
            details = self._get_image_details(task_id=task_id)
            status = details.get('status')
            success_flag = details.get('successFlag')

            if success_flag in (1, '1') or status in (1, 'completed', 'success'):
                return details

            if success_flag in (-1, 'failed') or status in (-1, 'failed', 'error') or details.get('errorCode'):
                raise KieAIClientResponseError(f'Kie.ai task {task_id} failed: {details}')

            logger.debug(
                'Kie.ai task %s pending (status=%s), attempt %s/%s',
                task_id, status or success_flag, attempt, max_attempts
            )
            time.sleep(delay)

        raise KieAIClientResponseError(f'Kie.ai task {task_id} did not complete in time')

    def _get_image_details(self, task_id: str) -> Dict[str, Any]:
        endpoint_url = self._build_url(self.status_endpoint)
        logger.debug('Fetching Kie.ai image details from %s', endpoint_url)

        try:
            response = self.session.get(
                endpoint_url,
                headers=self._headers(),
                params={'taskId': task_id},
                timeout=self.timeout
            )
        except requests.exceptions.RequestException as exc:
            raise KieAIClientError(f'Network error during OCR polling: {exc}') from exc
        except Exception as exc:  # pragma: no cover
            raise KieAIClientError(f'Unexpected error during OCR polling: {exc}') from exc

        data = self._handle_response(response)
        if isinstance(data, dict) and 'data' in data:
            return data['data']
        return data

    def extract_text(
        self,
        file_name: Optional[str],
        file_bytes: bytes,
        upload_path: Optional[str] = None,
        target_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience wrapper: upload → OCR.
        """
        effective_upload_path = upload_path or self.upload_path
        upload_data = self.upload_file(file_name=file_name, file_bytes=file_bytes, upload_path=effective_upload_path)
        recognition = self.recognize_image(
            download_url=upload_data['downloadUrl'],
            target_language=target_language
        )

        recognition['downloadUrl'] = upload_data['downloadUrl']
        recognition['fileName'] = upload_data.get('fileName') or file_name
        recognition['mimeType'] = upload_data.get('mimeType')
        return recognition

