from unittest import skip

from selenium.common.exceptions import NoAlertPresentException

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from mayan.apps.user_management.permissions import (
    permission_user_edit, permission_user_view
)
from mayan.apps.testing.tests.base import GenericViewTestCase
from mayan.apps.testing.tests.mixins import SeleniumTestMixin

from ..events import (
    event_theme_created, event_theme_edited, event_user_theme_settings_edited
)
from ..models import Theme
from ..permissions import (
    permission_theme_create, permission_theme_delete, permission_theme_edit,
    permission_theme_view
)

from .mixins import (
    ThemeTestMixin, ThemeViewTestMixin, UserThemeSettingsViewTestMixin
)


@skip('Skip until a synchronous live server class is added.')
class BasePlainViewTestCase(
    SeleniumTestMixin, StaticLiveServerTestCase, GenericViewTestCase
):
    auto_add_test_view = True
    test_view_url = r'^javascript:alert\("XSS"\)/$'
    test_view_is_public = True
    test_view_template = 'javascript_view'

    def test_login_view_url_fragment_xss(self):
        # Should redirect and not display an alert
        self._open_url(
            fragment='#javascript:alert("XSS")', viewname=settings.LOGIN_URL
        )

        with self.assertRaises(expected_exception=NoAlertPresentException):
            self.webdriver.switch_to_alert()

    def test_login_view_url_redirect(self):
        self._open_url(
            fragment='#javascript:alert("XSS")', viewname=settings.LOGIN_URL
        )

        self.assertTrue(self.test_view_template in self.webdriver.page_source)


class ThemeViewTestCase(
    ThemeTestMixin, ThemeViewTestMixin, GenericViewTestCase
):
    def test_theme_create_view_no_permission(self):
        theme_count = Theme.objects.count()

        self._clear_events()

        response = self._request_test_theme_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(Theme.objects.count(), theme_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_theme_create_view_with_permissions(self):
        self.grant_permission(permission=permission_theme_create)

        theme_count = Theme.objects.count()

        self._clear_events()

        response = self._request_test_theme_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Theme.objects.count(), theme_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_theme)
        self.assertEqual(events[0].verb, event_theme_created.id)

    def test_theme_delete_view_no_permission(self):
        self._create_test_theme()

        theme_count = Theme.objects.count()

        self._clear_events()

        response = self._request_test_theme_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(Theme.objects.count(), theme_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_theme_delete_view_with_access(self):
        self._create_test_theme()

        self.grant_access(
            obj=self._test_theme, permission=permission_theme_delete
        )

        theme_count = Theme.objects.count()

        self._clear_events()

        response = self._request_test_theme_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Theme.objects.count(), theme_count - 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_theme_edit_view_no_permission(self):
        self._create_test_theme()

        theme_label = self._test_theme.label

        self._clear_events()

        response = self._request_test_theme_edit_view()
        self.assertEqual(response.status_code, 404)

        self._test_theme.refresh_from_db()
        self.assertEqual(self._test_theme.label, theme_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_theme_edit_view_with_access(self):
        self._create_test_theme()

        self.grant_access(
            obj=self._test_theme, permission=permission_theme_edit
        )

        theme_label = self._test_theme.label

        self._clear_events()

        response = self._request_test_theme_edit_view()
        self.assertEqual(response.status_code, 302)

        self._test_theme.refresh_from_db()
        self.assertNotEqual(self._test_theme.label, theme_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_theme)
        self.assertEqual(events[0].verb, event_theme_edited.id)

    def test_theme_list_view_with_no_permission(self):
        self._create_test_theme()

        self._clear_events()

        response = self._request_test_theme_list_view()
        self.assertNotContains(
            response=response, text=self._test_theme.label, status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_theme_list_view_with_access(self):
        self._create_test_theme()

        self.grant_access(
            obj=self._test_theme, permission=permission_theme_view
        )

        self._clear_events()

        response = self._request_test_theme_list_view()
        self.assertContains(
            response=response, text=self._test_theme.label, status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class ThemeEffectViewTestCase(ThemeTestMixin, GenericViewTestCase):
    def test_normal_view_after_theme_delete(self):
        self._create_test_theme()

        self._test_case_user.theme_settings.theme = self._test_theme
        self._test_case_user.theme_settings.save()
        self._test_theme.delete()

        response = self.get(viewname='common:about_view')

        self.assertEqual(response.status_code, 200)


class CurrentUserViewTestCase(
    ThemeTestMixin, UserThemeSettingsViewTestMixin, GenericViewTestCase
):
    def setUp(self):
        super().setUp()
        self._create_test_theme()

    def test_current_user_theme_settings_detail_view_no_permission(self):
        self._clear_events()

        response = self._request_test_current_user_theme_settings_detail_view()
        self.assertEqual(response.status_code, 200)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_current_user_theme_settings_edit_view_no_permission(self):
        theme = self._test_case_user.theme_settings.theme

        self._clear_events()

        response = self._request_test_current_user_theme_settings_edit_view()
        self.assertEqual(response.status_code, 302)

        self._test_case_user.refresh_from_db()
        self.assertNotEqual(self._test_case_user.theme_settings.theme, theme)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_case_user)
        self.assertEqual(events[0].verb, event_user_theme_settings_edited.id)


class SuperUserThemeSettingsViewTestCase(
    ThemeTestMixin, UserThemeSettingsViewTestMixin, GenericViewTestCase
):
    def setUp(self):
        super().setUp()
        self._create_test_superuser()
        self._create_test_theme()

    def test_superuser_theme_settings_detail_view_no_permission(self):
        self._clear_events()

        response = self._request_test_superuser_theme_settings_detail_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_superuser_theme_settings_detail_view_with_access(self):
        self.grant_access(
            obj=self._test_superuser, permission=permission_user_view
        )

        self._clear_events()

        response = self._request_test_superuser_theme_settings_detail_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_superuser_theme_settings_edit_view_no_permission(self):
        theme = self._test_superuser.theme_settings.theme

        self._clear_events()

        response = self._request_test_superuser_theme_settings_edit_view()
        self.assertEqual(response.status_code, 404)

        self._test_superuser.refresh_from_db()
        self.assertEqual(self._test_superuser.theme_settings.theme, theme)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_superuser_theme_settings_edit_view_with_access(self):
        theme = self._test_superuser.theme_settings.theme

        self.grant_access(
            obj=self._test_superuser, permission=permission_user_edit
        )

        self._clear_events()

        response = self._request_test_superuser_theme_settings_edit_view()
        self.assertEqual(response.status_code, 404)

        self._test_superuser.refresh_from_db()
        self.assertEqual(self._test_superuser.theme_settings.theme, theme)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class UserThemeSettingsViewTestCase(
    ThemeTestMixin, UserThemeSettingsViewTestMixin, GenericViewTestCase
):
    auto_create_test_user = True

    def setUp(self):
        super().setUp()
        self._create_test_theme()

    def test_user_theme_settings_detail_view_no_permission(self):
        self._clear_events()

        response = self._request_test_user_theme_settings_detail_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_theme_settings_detail_view_with_access(self):
        self.grant_access(
            obj=self._test_user, permission=permission_user_view
        )

        self._clear_events()

        response = self._request_test_user_theme_settings_detail_view()
        self.assertEqual(response.status_code, 200)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_theme_settings_edit_view_no_permission(self):
        theme = self._test_user.theme_settings.theme

        self._clear_events()

        response = self._request_test_user_theme_settings_edit_view()
        self.assertEqual(response.status_code, 404)

        self._test_user.refresh_from_db()
        self.assertEqual(self._test_user.theme_settings.theme, theme)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_theme_settings_edit_view_with_access(self):
        theme = self._test_user.theme_settings.theme

        self.grant_access(
            obj=self._test_user, permission=permission_user_edit
        )

        self._clear_events()

        response = self._request_test_user_theme_settings_edit_view()
        self.assertEqual(response.status_code, 302)

        self._test_user.refresh_from_db()
        self.assertNotEqual(self._test_user.theme_settings.theme, theme)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user)
        self.assertEqual(events[0].verb, event_user_theme_settings_edited.id)
