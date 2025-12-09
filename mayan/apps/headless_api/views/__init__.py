# Views for Headless API endpoints

from mayan.apps.headless_api.views.activity_views import HeadlessActivityFeedView  # noqa: F401
from mayan.apps.headless_api.views.favorites_views import (  # noqa: F401
    HeadlessFavoriteListView,
    HeadlessFavoriteToggleView,
)
from mayan.apps.headless_api.views.version_views import HeadlessEditView  # noqa: F401
from mayan.apps.headless_api.views.my_uploads_views import HeadlessMyUploadsView  # noqa: F401