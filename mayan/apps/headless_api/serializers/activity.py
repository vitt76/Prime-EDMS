"""Serializers for headless activity feed."""

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class ActivityFeedSerializer(serializers.Serializer):
    """Flattened activity item for dashboard feed."""

    id = serializers.IntegerField()
    user = serializers.CharField()
    user_id = serializers.IntegerField(allow_null=True, required=False)
    action_text = serializers.CharField()
    object_name = serializers.CharField(allow_null=True, required=False)
    timestamp = serializers.DateTimeField()
    icon = serializers.CharField()
    verb = serializers.CharField()
    target_id = serializers.IntegerField(allow_null=True, required=False)

    VERB_MAP = {
        # documents
        'documents.document_create': (_('Загрузил файл'), 'upload'),
        'documents.document_download': (_('Скачал документ'), 'download'),
        'documents.document_new_version': (_('Загрузил новую версию'), 'upload'),
        'documents.document_view': (_('Открыл документ'), 'view'),
        'documents.document_file_created': (_('Добавил файл'), 'upload'),
        'documents.document_file_download': (_('Скачал файл'), 'download'),
        # metadata / tags / collections
        'documents.document_properties_edit': (_('Изменил свойства'), 'edit'),
        'documents.document_metadata_added': (_('Добавил метаданные'), 'tag'),
        'documents.document_metadata_edited': (_('Изменил метаданные'), 'tag'),
        'documents.document_tag_attach': (_('Добавил тег'), 'tag'),
        'documents.document_tag_remove': (_('Удалил тег'), 'tag'),
        'cabinets.cabinet_document_add': (_('Добавил в коллекцию'), 'collection'),
        'cabinets.cabinet_document_remove': (_('Удалил из коллекции'), 'collection'),
        # workflow / system
        'document_states.workflow_transition': (_('Изменил статус'), 'status'),
        'user_logged_in': (_('Вход в систему'), 'login'),
        'user_logged_out': (_('Выход из системы'), 'logout'),
    }

    def to_representation(self, action):
        action_text, icon = self._map_verb(action.verb)
        actor = getattr(action, 'actor', None)
        target = getattr(action, 'target', None)

        return {
            'id': action.pk,
            'user': getattr(actor, 'username', 'system') if actor else 'system',
            'user_id': actor.pk if actor else None,
            'action_text': action_text,
            'object_name': str(target) if target else None,
            'timestamp': action.timestamp,
            'icon': icon,
            'verb': action.verb,
            'target_id': getattr(target, 'pk', None)
        }

    def _map_verb(self, verb: str):
        """Return localized action text and icon for a verb."""
        if verb in self.VERB_MAP:
            mapped_text, icon = self.VERB_MAP[verb]
            return mapped_text, icon
        return verb, 'info'

