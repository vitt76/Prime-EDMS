from django.test import TestCase

from mayan.apps.organizations.patches import get_runtime_patch_status


class RuntimePatchStatusTestCase(TestCase):
    def test_runtime_patch_status_exposes_critical_entries(self):
        status = get_runtime_patch_status()

        self.assertIn('django.http.HttpRequest._current_scheme_host', status)
        self.assertIn('documents.Document.organization', status)
        self.assertIn('documents.Document.managers', status)
