"""
Indexing Metrics

Collects and reports metrics for document indexing operations.
"""
import logging
import time
from collections import defaultdict
from typing import Dict, Any

from django.core.cache import cache

logger = logging.getLogger(name=__name__)


class IndexingMetrics:
    """
    Collects and reports metrics for document indexing operations.
    
    Metrics are stored in Django cache with TTL for temporary storage.
    Metrics are logged periodically for monitoring.
    """
    
    CACHE_KEY_PREFIX = 'indexing_metrics_'
    CACHE_TTL = 3600  # 1 hour
    LOG_INTERVAL = 100  # Log metrics every N operations
    
    def __init__(self):
        self._operation_count = 0
        self._last_log_time = time.time()
    
    def record_index_success(self, document_id: int, duration: float = None):
        """Record a successful indexing operation."""
        self._operation_count += 1
        self._increment_counter('index_success')
        if duration:
            self._record_duration('index_duration', duration)
        self._maybe_log_metrics()
    
    def record_index_failure(self, document_id: int, error_type: str = None, duration: float = None):
        """Record a failed indexing operation."""
        self._operation_count += 1
        self._increment_counter('index_failure')
        if error_type:
            self._increment_counter(f'index_failure_{error_type}')
        if duration:
            self._record_duration('index_duration', duration)
        self._maybe_log_metrics()
    
    def record_deindex_success(self, document_id: int, duration: float = None):
        """Record a successful deindexing operation."""
        self._operation_count += 1
        self._increment_counter('deindex_success')
        if duration:
            self._record_duration('deindex_duration', duration)
        self._maybe_log_metrics()
    
    def record_deindex_failure(self, document_id: int, error_type: str = None, duration: float = None):
        """Record a failed deindexing operation."""
        self._operation_count += 1
        self._increment_counter('deindex_failure')
        if error_type:
            self._increment_counter(f'deindex_failure_{error_type}')
        if duration:
            self._record_duration('deindex_duration', duration)
        self._maybe_log_metrics()
    
    def record_retry(self, document_id: int, retry_count: int):
        """Record a retry operation."""
        self._increment_counter('retry_count')
        self._increment_counter(f'retry_count_{retry_count}')
    
    def _increment_counter(self, key: str):
        """Increment a counter metric."""
        cache_key = f'{self.CACHE_KEY_PREFIX}{key}'
        try:
            current = cache.get(cache_key, 0)
            cache.set(cache_key, current + 1, self.CACHE_TTL)
        except Exception as e:
            logger.debug('Error incrementing metric counter %s: %s', key, e)
    
    def _record_duration(self, key: str, duration: float):
        """Record a duration metric (average)."""
        cache_key_avg = f'{self.CACHE_KEY_PREFIX}{key}_avg'
        cache_key_count = f'{self.CACHE_KEY_PREFIX}{key}_count'
        try:
            current_avg = cache.get(cache_key_avg, 0.0)
            current_count = cache.get(cache_key_count, 0)
            
            # Calculate new average
            new_avg = ((current_avg * current_count) + duration) / (current_count + 1)
            
            cache.set(cache_key_avg, new_avg, self.CACHE_TTL)
            cache.set(cache_key_count, current_count + 1, self.CACHE_TTL)
        except Exception as e:
            logger.debug('Error recording metric duration %s: %s', key, e)
    
    def _maybe_log_metrics(self):
        """Log metrics periodically."""
        current_time = time.time()
        if (self._operation_count % self.LOG_INTERVAL == 0 or
            current_time - self._last_log_time > 300):  # Log every 5 minutes
            self._log_metrics()
            self._last_log_time = current_time
    
    def _log_metrics(self):
        """Log current metrics."""
        try:
            metrics = self.get_metrics()
            logger.info(
                'Indexing metrics: %d operations, %d success, %d failures, '
                'avg index duration: %.2fs, avg deindex duration: %.2fs',
                metrics.get('total_operations', 0),
                metrics.get('index_success', 0),
                metrics.get('index_failure', 0),
                metrics.get('index_duration_avg', 0.0),
                metrics.get('deindex_duration_avg', 0.0)
            )
            
            # Log error breakdown
            error_types = metrics.get('error_types', {})
            if error_types:
                logger.debug('Indexing error breakdown: %s', error_types)
        except Exception as e:
            logger.debug('Error logging metrics: %s', e)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            dict: Current metrics including counters, durations, and error types
        """
        metrics = {}
        
        # Get all counter metrics
        counter_keys = [
            'index_success', 'index_failure', 'deindex_success', 'deindex_failure',
            'retry_count'
        ]
        
        for key in counter_keys:
            cache_key = f'{self.CACHE_KEY_PREFIX}{key}'
            metrics[key] = cache.get(cache_key, 0)
        
        # Get duration metrics
        duration_keys = ['index_duration', 'deindex_duration']
        for key in duration_keys:
            cache_key_avg = f'{self.CACHE_KEY_PREFIX}{key}_avg'
            cache_key_count = f'{self.CACHE_KEY_PREFIX}{key}_count'
            metrics[f'{key}_avg'] = cache.get(cache_key_avg, 0.0)
            metrics[f'{key}_count'] = cache.get(cache_key_count, 0)
        
        # Calculate total operations
        metrics['total_operations'] = (
            metrics.get('index_success', 0) +
            metrics.get('index_failure', 0) +
            metrics.get('deindex_success', 0) +
            metrics.get('deindex_failure', 0)
        )
        
        # Get error type breakdown
        error_types = {}
        for key in ['index_failure', 'deindex_failure']:
            base_count = metrics.get(key, 0)
            if base_count > 0:
                # Try to get error type breakdown
                for error_type in ['trashed', 'not_found', 'stub', 'scheduling_error']:
                    error_key = f'{key}_{error_type}'
                    cache_key = f'{self.CACHE_KEY_PREFIX}{error_key}'
                    error_count = cache.get(cache_key, 0)
                    if error_count > 0:
                        if error_type not in error_types:
                            error_types[error_type] = 0
                        error_types[error_type] += error_count
        
        if error_types:
            metrics['error_types'] = error_types
        
        return metrics
    
    def reset_metrics(self):
        """Reset all metrics (for testing or manual reset)."""
        # This would require iterating through all possible keys
        # For now, just log a warning
        logger.warning('Metrics reset requested - this requires manual cache clearing')
    
    def get_total_indexed(self) -> int:
        """Get total number of successfully indexed documents."""
        return self.get_metrics().get('index_success', 0)
    
    def get_total_failed(self) -> int:
        """Get total number of failed indexing operations."""
        return self.get_metrics().get('index_failure', 0)
    
    def get_total_retries(self) -> int:
        """Get total number of retry operations."""
        return self.get_metrics().get('retry_count', 0)
    
    def get_avg_duration(self) -> float:
        """Get average indexing duration in seconds."""
        return self.get_metrics().get('index_duration_avg', 0.0)


# Global metrics instance
_metrics_instance = None


def get_metrics() -> IndexingMetrics:
    """Get the global metrics instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = IndexingMetrics()
    return _metrics_instance

