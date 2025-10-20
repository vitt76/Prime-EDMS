from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from ..models import Recipient, RecipientList, RenditionPreset


class RecipientSerializer(serializers.ModelSerializer):
    presets = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'email', 'name', 'organization', 'locale', 'presets',
            'created', 'modified'
        )
        model = Recipient
        read_only_fields = ('id', 'created', 'modified')

    def get_presets(self, obj):
        presets = RenditionPreset.objects.filter(recipient=obj)
        return [{'id': preset.id, 'name': preset.name} for preset in presets]

    def create(self, validated_data):
        validated_data.pop('_instance_extra_data', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('_instance_extra_data', None)
        return super().update(instance, validated_data)


class RecipientListSerializer(serializers.ModelSerializer):
    recipients = RecipientSerializer(many=True, read_only=True)
    recipients_id_list = serializers.ListField(
        child=serializers.IntegerField(),
        help_text=_('List of recipient IDs to add to this list.'),
        required=False, write_only=True
    )
    internal_users_id_list = serializers.ListField(
        child=serializers.IntegerField(),
        help_text=_('List of internal user IDs to add to this list.'),
        required=False, write_only=True
    )

    class Meta:
        fields = (
            'id', 'name', 'owner', 'recipients', 'internal_users',
            'recipients_id_list', 'internal_users_id_list',
            'created', 'modified'
        )
        model = RecipientList
        read_only_fields = ('id', 'created', 'modified')

    def create(self, validated_data):
        validated_data.pop('_instance_extra_data', None)
        recipients_id_list = validated_data.pop('recipients_id_list', [])
        internal_users_id_list = validated_data.pop('internal_users_id_list', [])

        instance = super().create(validated_data)

        if recipients_id_list:
            recipients = Recipient.objects.filter(id__in=recipients_id_list)
            instance.recipients.set(recipients)

        if internal_users_id_list:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(id__in=internal_users_id_list)
            instance.internal_users.set(users)

        return instance

    def update(self, instance, validated_data):
        validated_data.pop('_instance_extra_data', None)
        recipients_id_list = validated_data.pop('recipients_id_list', None)
        internal_users_id_list = validated_data.pop('internal_users_id_list', None)

        instance = super().update(instance, validated_data)

        if recipients_id_list is not None:
            recipients = Recipient.objects.filter(id__in=recipients_id_list)
            instance.recipients.set(recipients)

        if internal_users_id_list is not None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(id__in=internal_users_id_list)
            instance.internal_users.set(users)

        return instance
