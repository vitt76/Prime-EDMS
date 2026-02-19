"""
Phase 5 Backend verification: Orientation, Recently Viewed, Saved Searches.

Creates minimal test data and runs API checks using DRF test client.

Run (from project root, with virtualenv activated):
  python manage.py verify_phase5

Windows PowerShell (if venv is in parent folder, e.g. C:\\DAM\\.venv311):
  ..\\.venv311\\Scripts\\Activate.ps1
  python manage.py verify_phase5

Docker (after applying migrations: mayan-edms.py migrate):
  docker exec prime-edms_app_1 /opt/mayan-edms/bin/mayan-edms.py verify_phase5

Requires: migrations applied (documents 0087, saved_searches 0001), organizations app.
"""

import logging

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verify Phase 5 APIs: recently-viewed, orientation filter, saved-searches CRUD and run'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-create',
            action='store_true',
            help='Skip creating test data; only run API checks (requires existing data)',
        )

    def handle(self, *args, **options):
        no_create = options['no_create']
        self.stdout.write(self.style.WARNING('Phase 5 API verification'))
        self.stdout.write('=' * 60)

        # Paths: API is mounted at /api/, then v4/ from api_version_urls
        api_prefix = '/api/v4'
        headless_prefix = api_prefix + '/headless'
        recently_viewed_path = headless_prefix + '/documents/recently-viewed/'
        saved_searches_path = headless_prefix + '/saved-searches/'
        optimized_list_path = api_prefix + '/documents/optimized/'

        user = None
        organization = None
        doc = None
        doc_id = None
        if not no_create:
            self.stdout.write('Creating test data...')
            user, organization, doc, doc_id = self._create_test_data()
            if not doc_id:
                self.stdout.write(self.style.ERROR('Could not create test document'))
                return
            self.stdout.write(self.style.SUCCESS('Created user, org, document (id=%s)' % doc_id))
        else:
            from django.contrib.auth import get_user_model
            from mayan.apps.organizations.models import Organization
            from mayan.apps.documents.models import Document
            User = get_user_model()
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            organization = Organization.objects.first()
            doc = Document.valid.filter(organization=organization).first()
            if not user or not organization:
                self.stdout.write(self.style.ERROR('Need at least one user and organization (run without --no-create)'))
                return
            doc_id = doc.pk if doc else None

        client = APIClient()
        client.force_authenticate(user=user)

        # Test 1: Recently viewed
        self.stdout.write('Test 1: GET recently-viewed...')
        rv_resp = client.get(
            recently_viewed_path,
            HTTP_X_ORGANIZATION_ID=str(organization.pk),
        )
        if rv_resp.status_code in (200, 400):
            data = getattr(rv_resp, 'data', None) or (rv_resp.json() if hasattr(rv_resp, 'json') else {})
            if rv_resp.status_code == 400 and 'Organization' in str(data):
                self.stdout.write(self.style.WARNING('  Recently-viewed returned 400 (organization context) - middleware may be needed in test'))
            else:
                count = data.get('count', 0) if isinstance(data, dict) else 0
                self.stdout.write(self.style.SUCCESS('  Recently-viewed: count=%s' % count))
        else:
            self.stdout.write(self.style.ERROR('  Recently-viewed failed: %s' % rv_resp.status_code))

        # Test 2: Orientation filter
        self.stdout.write('Test 2: GET optimized list orientation=landscape...')
        opt_resp = client.get(
            optimized_list_path,
            {'orientation': 'landscape', 'page_size': '5'},
            HTTP_X_ORGANIZATION_ID=str(organization.pk),
        )
        if opt_resp.status_code == 200:
            data = getattr(opt_resp, 'data', None) or opt_resp.json()
            results = data.get('results', data) if isinstance(data, dict) else []
            self.stdout.write(self.style.SUCCESS('  Orientation filter: %s results' % len(results)))
        else:
            self.stdout.write(self.style.WARNING('  Optimized list: %s (check URL and permissions)' % opt_resp.status_code))

        # Test 3: Saved search POST then run
        self.stdout.write('Test 3: POST saved-searches, then GET run/...')
        post_resp = client.post(
            saved_searches_path,
            {'name': 'Phase5 verify search', 'query': 'test', 'filters': {'orientation': 'landscape'}},
            HTTP_X_ORGANIZATION_ID=str(organization.pk),
            format='json',
        )
        if post_resp.status_code in (200, 201):
            data = getattr(post_resp, 'data', None) or post_resp.json()
            sid = data.get('id')
            if sid:
                run_resp = client.get(
                    saved_searches_path + '%s/run/' % sid,
                    HTTP_X_ORGANIZATION_ID=str(organization.pk),
                )
                if run_resp.status_code == 200:
                    run_data = getattr(run_resp, 'data', None) or run_resp.json()
                    run_count = run_data.get('count', 0) if isinstance(run_data, dict) else 0
                    self.stdout.write(self.style.SUCCESS('  Saved search run: count=%s' % run_count))
                else:
                    self.stdout.write(self.style.ERROR('  Run failed: %s' % run_resp.status_code))
            else:
                self.stdout.write(self.style.ERROR('  No id in POST response'))
        else:
            self.stdout.write(self.style.ERROR('  POST saved-searches failed: %s' % post_resp.status_code))

        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('Verification finished. Review output above.'))

    def _create_test_data(self):
        from django.contrib.auth import get_user_model
        from mayan.apps.organizations.models import Organization
        from mayan.apps.documents.models import Document, DocumentFile, DocumentType
        from mayan.apps.analytics.models import AssetEvent
        from mayan.apps.acls.models import AccessControlList
        from mayan.apps.permissions import Permission
        from mayan.apps.documents.permissions import permission_document_view

        User = get_user_model()
        organization = Organization.objects.first()
        if not organization:
            self.stdout.write(self.style.ERROR('No organization in DB. Create one first.'))
            return None, None, None, None

        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No user in DB.'))
            return None, None, None, None

        doc_type = DocumentType.objects.first()
        if not doc_type:
            doc_type = DocumentType.objects.create(label='Verify Phase5')

        doc = Document.objects.create(
            label='Phase5 Verify Landscape',
            document_type=doc_type,
            organization=organization,
        )
        try:
            df = DocumentFile(document=doc, filename='verify.jpg')
            df.file.save('verify_phase5.jpg', ContentFile(b'\xff\xd8\xff'), save=True)
            df.width = 1920
            df.height = 1080
            df.save()
        except Exception as e:
            self.stdout.write(self.style.WARNING('DocumentFile create: %s (orientation test may use existing docs)' % e))
            doc.delete()
            return user, organization, None, None

        AssetEvent.objects.create(
            organization=organization,
            document=doc,
            user=user,
            event_type=AssetEvent.EVENT_TYPE_VIEW,
            timestamp=timezone.now(),
        )

        try:
            acl = AccessControlList.objects.get_for_object(doc)
            acl.grant(permission=permission_document_view, role=None, user=user)
        except Exception:
            pass

        return user, organization, doc, doc.pk
