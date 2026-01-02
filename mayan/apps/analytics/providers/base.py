"""Provider base class for external analytics integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAnalyticsProvider(ABC):
    """Adapter/Strategy interface for external analytics sources."""

    provider_id: str = ''
    display_name: str = ''
    channel: str = ''  # normalized channel identifier, e.g. 'youtube'

    @abstractmethod
    def fetch_metrics(self, *, asset_id: int) -> Dict[str, Any]:
        """Fetch external metrics for a DAM asset (Document).

        Args:
            asset_id: DAM Document ID.

        Returns:
            Dict with normalized metrics fields (mockable):
                - views (int)
                - clicks (int)
                - conversions (int)
                - bandwidth_bytes (int)
                - latency_ms (int)
                - external_id (str)
                - sync_status (str)
                - last_sync_error (str)
                - retry_count (int)
                - metadata (dict)
        """

    @abstractmethod
    def push_event(self, *, event: Dict[str, Any]) -> Optional[str]:
        """Push a DAM event to the external system (if supported).

        Returns:
            Optional external event id.
        """


