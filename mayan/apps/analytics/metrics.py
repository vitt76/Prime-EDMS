"""Prometheus metrics for analytics module."""

from __future__ import annotations

from prometheus_client import Counter, Gauge


analytics_events_processed_total = Counter(
    'analytics_events_processed_total',
    'Total number of analytics events persisted by the consumer',
    ['kind'],
)

analytics_redis_stream_lag = Gauge(
    'analytics_redis_stream_lag',
    'Current Redis Streams length for analytics stream (best-effort)',
)


