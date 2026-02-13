"""Serializers for analytics API (tenant-scoped dashboard)."""

from rest_framework import serializers


class AIUsageSerializer(serializers.Serializer):
    """Read-only AI usage metrics for dashboard."""

    count_this_month = serializers.IntegerField(read_only=True)
    token_usage = serializers.IntegerField(read_only=True, allow_null=True)


class DashboardMetricsSerializer(serializers.Serializer):
    """Read-only tenant-scoped dashboard metrics (single response)."""

    organization = serializers.CharField(read_only=True)
    organization_name = serializers.CharField(read_only=True)
    total_documents = serializers.IntegerField(read_only=True)
    storage_used_gb = serializers.FloatField(read_only=True)
    active_users_30d = serializers.IntegerField(read_only=True)
    top_documents = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    ai_usage = AIUsageSerializer(read_only=True, allow_null=True)
