"""
Throttling classes for distribution API endpoints.

Distribution endpoints need higher rate limits because:
- Pages may load multiple resources simultaneously (share links, campaigns, etc.)
- Users may refresh data frequently during active work sessions
- Bulk operations may require multiple API calls
"""
from rest_framework.throttling import UserRateThrottle


class DistributionThrottle(UserRateThrottle):
    """
    Relaxed throttling for distribution API endpoints.
    
    Rate limits:
    - 200 requests per minute (allows rapid page loads)
    - 10000 requests per hour (prevents abuse while allowing normal usage)
    
    This is more permissive than the default UserRateThrottle to prevent
    429 errors during normal usage patterns like:
    - Loading sharing page with multiple API calls
    - Refreshing campaign data
    - Loading share link lists with previews
    """
    scope = 'distribution'

