from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers

from ..models import Recipient, RecipientList


class RecipientSerializer(serializers.HyperlinkedModelSerializer):
    recipient_lists_url = serializers.HyperlinkedIdentityField(
        lookup_url_kwarg='recipient_id',
        view_name='rest_api:recipient-list'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'recipient_id',
                'view_name': 'rest_api:recipient-detail'
            }
        }
        fields = (
            'id', 'email', 'name', 'organization', 'locale',
            'created', 'modified', 'url', 'recipient_lists_url'
        )
        model = Recipient
        read_only_fields = ('id', 'created', 'modified')


class RecipientListSerializer(serializers.HyperlinkedModelSerializer):
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
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'recipient_list_id',
                'view_name': 'rest_api:recipientlist-detail'
            }
        }
        fields = (
            'id', 'name', 'owner', 'recipients', 'internal_users',
            'recipients_id_list', 'internal_users_id_list',
            'created', 'modified', 'url'
        )
        model = RecipientList
        read_only_fields = ('id', 'created', 'modified')

    def create(self, validated_data):
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
        recipients_id_list = validated_data.pop('recipients_id_list', [])
        internal_users_id_list = validated_data.pop('internal_users_id_list', [])

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
