"""
Tests for quota enforcement utilities.

Sprint 4: Comprehensive test coverage for quota checks,
QuotaExceededException, and signal handler.
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from mayan.apps.organizations.models import (
    Organization, UserOrganizationRole
)
from mayan.apps.organizations.quota import (
    QuotaExceededException,
    check_ai_quota,
    check_storage_quota,
    check_user_quota,
    on_document_file_pre_save,
)

User = get_user_model()


class QuotaExceededExceptionTestCase(TestCase):
    """Tests for QuotaExceededException."""

    def setUp(self):
        self.org = Organization.objects.create(
            name='Quota Org', slug='quota-org', email='q@test.com',
            is_active=True, status='active'
        )

    def test_exception_attributes(self):
        """Exception stores quota_type, org, values, and http_status."""
        exc = QuotaExceededException(
            quota_type='storage',
            organization=self.org,
            current_value=100,
            limit_value=50,
            http_status=402
        )
        self.assertEqual(exc.quota_type, 'storage')
        self.assertEqual(exc.organization, self.org)
        self.assertEqual(exc.current_value, 100)
        self.assertEqual(exc.limit_value, 50)
        self.assertEqual(exc.http_status, 402)

    def test_exception_message(self):
        """Exception message includes quota type and org name."""
        exc = QuotaExceededException(
            quota_type='users',
            organization=self.org,
            current_value=10,
            limit_value=5,
            http_status=429
        )
        self.assertIn('users', str(exc))
        self.assertIn('Quota Org', str(exc))

    def test_default_http_status(self):
        """Default HTTP status is 429."""
        exc = QuotaExceededException(
            quota_type='ai_analyses',
            organization=self.org,
            current_value=0,
            limit_value=0
        )
        self.assertEqual(exc.http_status, 429)


class CheckStorageQuotaTestCase(TestCase):
    """Tests for check_storage_quota()."""

    def setUp(self):
        self.org = Organization.objects.create(
            name='Storage Org', slug='storage-org', email='s@test.com',
            is_active=True, status='active',
            storage_limit_gb=100
        )

    def test_within_limit(self):
        """No exception when storage is within limit."""
        with patch.object(
            Organization, 'get_storage_used_gb', return_value=50.0
        ):
            check_storage_quota(self.org)  # Should not raise

    def test_exceeded_raises(self):
        """QuotaExceededException raised when storage exceeds limit."""
        with patch.object(
            Organization, 'get_storage_used_gb', return_value=100.0
        ):
            with self.assertRaises(QuotaExceededException) as ctx:
                check_storage_quota(self.org)
            self.assertEqual(ctx.exception.quota_type, 'storage')
            self.assertEqual(ctx.exception.http_status, 402)

    def test_unlimited_storage(self):
        """No exception when storage_limit_gb is None (unlimited)."""
        self.org.storage_limit_gb = None
        self.org.save(update_fields=['storage_limit_gb'])
        check_storage_quota(self.org)  # Should not raise

    def test_none_organization(self):
        """No exception when organization is None."""
        check_storage_quota(None)  # Should not raise


class CheckUserQuotaTestCase(TestCase):
    """Tests for check_user_quota()."""

    def setUp(self):
        self.org = Organization.objects.create(
            name='User Org', slug='user-org', email='u@test.com',
            is_active=True, status='active',
            max_users=3
        )
        # Create 2 members
        for i in range(2):
            user = User.objects.create_user(
                username='user_{}'.format(i), password='pass123'
            )
            UserOrganizationRole.objects.create(
                user=user, organization=self.org,
                role=UserOrganizationRole.ROLE_MEMBER
            )

    def test_within_limit(self):
        """No exception when user count is within limit."""
        check_user_quota(self.org)  # 2 members, limit 3

    def test_exceeded_raises(self):
        """QuotaExceededException raised when limit exceeded."""
        # Add third member to hit the limit
        user3 = User.objects.create_user(
            username='user_3', password='pass123'
        )
        UserOrganizationRole.objects.create(
            user=user3, organization=self.org,
            role=UserOrganizationRole.ROLE_MEMBER
        )
        with self.assertRaises(QuotaExceededException) as ctx:
            check_user_quota(self.org)
        self.assertEqual(ctx.exception.quota_type, 'users')
        self.assertEqual(ctx.exception.current_value, 3)
        self.assertEqual(ctx.exception.limit_value, 3)

    def test_none_organization(self):
        """No exception when organization is None."""
        check_user_quota(None)  # Should not raise


class CheckAIQuotaTestCase(TestCase):
    """Tests for check_ai_quota()."""

    def setUp(self):
        self.org = Organization.objects.create(
            name='AI Org', slug='ai-org', email='ai@test.com',
            is_active=True, status='active',
            max_ai_analyses_monthly=10
        )

    def test_within_limit(self):
        """No exception when AI analysis count is within limit."""
        with patch.object(
            Organization, 'get_ai_analyses_this_month', return_value=5
        ):
            check_ai_quota(self.org)

    def test_exceeded_raises(self):
        """QuotaExceededException raised when monthly limit exceeded."""
        with patch.object(
            Organization, 'get_ai_analyses_this_month', return_value=10
        ):
            with self.assertRaises(QuotaExceededException) as ctx:
                check_ai_quota(self.org)
            self.assertEqual(ctx.exception.quota_type, 'ai_analyses')
            self.assertEqual(ctx.exception.http_status, 429)

    def test_none_organization(self):
        """No exception when organization is None."""
        check_ai_quota(None)  # Should not raise


class DocumentFilePreSaveSignalTestCase(TestCase):
    """Tests for on_document_file_pre_save signal handler."""

    def setUp(self):
        self.org = Organization.objects.create(
            name='Signal Org', slug='signal-org', email='sig@test.com',
            is_active=True, status='active',
            storage_limit_gb=1
        )

    def test_skips_existing_files(self):
        """Signal handler skips files that already have pk."""
        instance = MagicMock()
        instance.pk = 123  # Existing file
        # Should not raise even if quota is exceeded
        on_document_file_pre_save(sender=None, instance=instance)

    def test_blocks_new_file_when_quota_exceeded(self):
        """Signal handler blocks new file when storage quota exceeded."""
        instance = MagicMock()
        instance.pk = None  # New file
        instance.document.organization = self.org

        with patch.object(
            Organization, 'get_storage_used_gb', return_value=2.0
        ):
            with self.assertRaises(QuotaExceededException):
                on_document_file_pre_save(sender=None, instance=instance)

    def test_allows_new_file_within_quota(self):
        """Signal handler allows new file when storage is within quota."""
        instance = MagicMock()
        instance.pk = None
        instance.document.organization = self.org

        with patch.object(
            Organization, 'get_storage_used_gb', return_value=0.5
        ):
            on_document_file_pre_save(
                sender=None, instance=instance
            )  # Should not raise

    def test_skips_when_no_organization(self):
        """Signal handler skips when document has no organization."""
        instance = MagicMock()
        instance.pk = None
        instance.document.organization = None
        on_document_file_pre_save(
            sender=None, instance=instance
        )  # Should not raise
