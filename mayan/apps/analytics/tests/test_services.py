from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from mayan.apps.documents.models import Document, DocumentType

from mayan.apps.analytics.models import AssetEvent, SearchQuery, SearchSession
from mayan.apps.analytics.services import link_download_to_latest_search_session


User = get_user_model()


class SearchToFindLinkingTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='u1', password='test')
        self.document_type = DocumentType.objects.create(label='T1')
        self.document = Document.objects.create(document_type=self.document_type, label='D1')

    def test_link_download_to_latest_search_session(self):
        started_at = timezone.now() - timezone.timedelta(minutes=10)

        session = SearchSession.objects.create(user=self.user, started_at=started_at)
        query = SearchQuery.objects.create(
            user=self.user,
            query_text='test',
            search_type=SearchQuery.SEARCH_TYPE_KEYWORD,
            results_count=5,
            response_time_ms=123,
            filters_applied={},
            user_department='',
            search_session_id=session.pk
        )

        # Normalize timestamps for deterministic delta.
        SearchQuery.objects.filter(pk=query.pk).update(timestamp=started_at)
        SearchSession.objects.filter(pk=session.pk).update(first_search_query=query)

        download_ts = timezone.now()
        download_event = AssetEvent.objects.create(
            document=self.document,
            event_type=AssetEvent.EVENT_TYPE_DOWNLOAD,
            user=self.user,
            channel='dam_interface',
        )
        AssetEvent.objects.filter(pk=download_event.pk).update(timestamp=download_ts)
        download_event.refresh_from_db()

        linked = link_download_to_latest_search_session(user=self.user, download_event=download_event, max_window_minutes=30)

        self.assertIsNotNone(linked)

        session.refresh_from_db()
        self.assertIsNotNone(session.ended_at)
        self.assertIsNotNone(session.time_to_find_seconds)
        self.assertEqual(session.last_download_event_id, download_event.pk)

        query.refresh_from_db()
        self.assertTrue(query.was_downloaded)
        self.assertIsNotNone(query.time_to_download_seconds)


