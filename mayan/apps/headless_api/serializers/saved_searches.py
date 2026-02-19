"""Serializers for headless Saved Searches API (Phase 5.3)."""

from rest_framework import serializers

from mayan.apps.saved_searches.models import SavedSearch

# Limit saved searches per user (plan: e.g. 20)
SAVED_SEARCH_MAX_PER_USER = 20


class SavedSearchSerializer(serializers.ModelSerializer):
    """Serializer for SavedSearch: list and CRUD."""

    class Meta:
        model = SavedSearch
        fields = ('id', 'name', 'query', 'filters', 'created_at', 'notification_enabled', 'last_notified_at')
        read_only_fields = ('id', 'created_at', 'last_notified_at')

    def validate_name(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Name is required.')
        return (value or '').strip()

    def validate_filters(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError('Filters must be a JSON object.')
        return value

    def validate(self, attrs):
        # Enforce per-user limit on create
        if not self.instance and self.context.get('request'):
            user = self.context['request'].user
            organization = getattr(self.context['request'], 'organization', None)
            if organization is not None:
                count = SavedSearch.objects.filter(user=user, organization=organization).count()
                if count >= SAVED_SEARCH_MAX_PER_USER:
                    raise serializers.ValidationError(
                        {'name': f'Maximum {SAVED_SEARCH_MAX_PER_USER} saved searches per user.'}
                    )
        return attrs
