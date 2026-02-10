"""
Reusable queryset helpers for the Organizations app.

Provides annotation helpers to avoid duplicating Count/Q expressions
across views, mixins, and admin classes.
"""

from django.db.models import Count, Q


def annotate_org_counts(queryset):
    """
    Annotate an Organization queryset with ``member_count``.

    ``member_count`` is the number of active users associated with
    the organization (i.e. ``members`` with ``is_active=True``).

    Usage::

        qs = annotate_org_counts(
            Organization.objects.select_related('owner')
        )
    """
    return queryset.annotate(
        member_count=Count(
            'members', filter=Q(members__is_active=True)
        ),
    )
