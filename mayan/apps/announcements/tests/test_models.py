from datetime import timedelta

from django.utils import timezone

from mayan.apps.testing.tests.base import BaseTestCase

from ..models import Announcement

from .mixins import AnnouncementTestMixin


class AnnouncementModelTestCase(AnnouncementTestMixin, BaseTestCase):
    def setUp(self):
        super().setUp()
        self._create_test_announcement()

    def test_basic(self):
        queryset = Announcement.objects.get_for_now()

        self.assertEqual(queryset.exists(), True)

    def test_end_datetime(self):
        self._test_announcement.start_datetime = timezone.now() - timedelta(days=2)
        self._test_announcement.end_datetime = timezone.now() - timedelta(days=1)
        self._test_announcement.save()

        queryset = Announcement.objects.get_for_now()

        self.assertEqual(queryset.exists(), False)

    def test_enable(self):
        self._test_announcement.enabled = False
        self._test_announcement.save()

        queryset = Announcement.objects.get_for_now()

        self.assertEqual(queryset.exists(), False)

    def test_start_datetime(self):
        self._test_announcement.start_datetime = timezone.now() - timedelta(days=1)
        self._test_announcement.save()

        queryset = Announcement.objects.get_for_now()

        self.assertEqual(queryset.first(), self._test_announcement)

    def test_method_get_absolute_url(self):
        self.assertTrue(self._test_announcement.get_absolute_url())
