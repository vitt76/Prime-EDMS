from unittest import TestCase
from unittest.mock import MagicMock, patch

from mayan.apps.dam.ai_providers.kieai import KieAIProvider
from mayan.apps.dam.services.kie_ai_client import (
    KieAIClient,
    KieAIClientError,
    KieAIClientResponseError,
)


class KieAIClientTests(TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.client = KieAIClient(
            api_key='secret',
            base_url='https://kie.ai/',
            upload_url='https://kie.ai/api/file-stream-upload',
            ocr_endpoint='generate',
            status_endpoint='record-info',
            session=self.session
        )

    def test_upload_file_success(self):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'downloadUrl': 'https://cdn/k/file.png', 'fileName': 'file.png'}
        }
        self.session.post.return_value = mock_response

        data = self.client.upload_file('file.png', b'binary', upload_path='tmp')

        self.assertEqual(data['downloadUrl'], 'https://cdn/k/file.png')
        self.session.post.assert_called_once()

    def test_upload_file_missing_url(self):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'success': True, 'data': {}}
        self.session.post.return_value = mock_response

        with self.assertRaises(KieAIClientResponseError):
            self.client.upload_file('file.png', b'data')

    def test_recognize_image_success_flow(self):
        # upload response
        mock_upload_response = MagicMock()
        mock_upload_response.ok = True
        mock_upload_response.json.return_value = {
            'success': True,
            'data': {'downloadUrl': 'https://cdn/k/file.png'}
        }

        # start job response
        mock_job_response = MagicMock()
        mock_job_response.ok = True
        mock_job_response.json.return_value = {
            'success': True,
            'data': {'taskId': '123'}
        }

        # details response
        mock_details_response = MagicMock()
        mock_details_response.ok = True
        mock_details_response.json.return_value = {
            'success': True,
            'data': {'status': 1, 'successFlag': 1, 'content': 'описание', 'language': 'ru'}
        }

        self.session.post.side_effect = [
            mock_upload_response,
            mock_job_response
        ]
        self.session.get.return_value = mock_details_response

        result = self.client.extract_text('file.png', b'data')
        self.assertEqual(result['text'], 'описание')
        self.assertEqual(result['language'], 'ru')
        self.assertEqual(result['downloadUrl'], 'https://cdn/k/file.png')

    def test_recognize_image_network_error(self):
        self.session.post.side_effect = Exception('boom')

        with self.assertRaises(KieAIClientError):
            self.client.recognize_image('https://cdn/file.png')


class KieAIProviderTests(TestCase):
    @patch('mayan.apps.dam.ai_providers.kieai.KieAIClient')
    def test_analyze_image_returns_expected_payload(self, client_cls):
        mock_client = MagicMock()
        mock_client.extract_text.return_value = {
            'text': 'Some OCR text',
            'language': 'ru',
            'downloadUrl': 'https://cdn/file.png'
        }
        client_cls.return_value = mock_client

        provider = KieAIProvider(
            api_key='secret',
            base_url='https://kie.ai/'
        )

        result = provider.analyze_image(b'data', 'image/png')

        self.assertEqual(result['description'], 'Some OCR text')
        self.assertIn('ocr', result['categories'])
        self.assertEqual(result['language'], 'ru')
        mock_client.extract_text.assert_called_once()

