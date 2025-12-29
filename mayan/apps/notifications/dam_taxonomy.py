"""DAM notification taxonomy.

This module defines the allowlist of event types that are considered part of the
DAM Notification Center for non-admin users.

We intentionally do NOT expose the full Mayan EDMS events log to regular users.
Admins will have a separate Admin Logs view (full activity + system events).

The values in this file are based on actual Mayan event `Action.verb` values,
e.g. `documents.document_version_created`, and can be extended as DAM features
introduce new event namespaces (ai.*, distribution.*, comments.*, etc.).
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Literal, Optional


NotificationCategory = Literal[
    'uploads',
    'processing',
    'views',
    'downloads',
    'lifecycle',
    # Reserved categories for future DAM features:
    'ai',
    'distribution',
    'comments',
    'access',
]


# NOTE: This is the authoritative mapping used by the Headless Notifications API.
# Keep this list curated; do not add noisy internal/system verbs here.
EVENT_TYPE_TO_CATEGORY: Dict[str, NotificationCategory] = {
    # Upload / ingest
    'documents.document_create': 'uploads',
    'documents.document_file_created': 'uploads',

    # Processing / versioning pipeline
    'documents.document_version_created': 'processing',
    'documents.document_version_page_created': 'processing',

    # User interactions (optional; keep minimal to avoid noise)
    'documents.document_view': 'views',
    'documents.document_file_downloaded': 'downloads',

    # Lifecycle events (trash/restore/delete)
    'documents.document_trashed': 'lifecycle',
    'documents.trashed_document_restored': 'lifecycle',
    'documents.trashed_document_deleted': 'lifecycle',
}


DAM_EVENT_TYPES_ALLOWLIST: FrozenSet[str] = frozenset(EVENT_TYPE_TO_CATEGORY.keys())


def is_dam_event_type(*, event_type: str) -> bool:
    """Return True if the event type is part of the DAM Notification Center."""

    return event_type in DAM_EVENT_TYPES_ALLOWLIST


def get_dam_category(*, event_type: str) -> Optional[NotificationCategory]:
    """Return the category for an event type or None if not a DAM event."""

    return EVENT_TYPE_TO_CATEGORY.get(event_type)


