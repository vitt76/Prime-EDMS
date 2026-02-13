import json
import logging
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

# Close code when user is not in the requested organization
WS_CLOSE_ORG_DENIED = 4003


@sync_to_async
def _get_user_from_token(token_string: str):
    """Resolve DRF TokenAuthentication key into a Django user."""

    try:
        from rest_framework.authtoken.models import Token
    except Exception:
        return AnonymousUser()

    try:
        token = Token.objects.select_related('user').get(key=token_string)
    except Token.DoesNotExist:
        return AnonymousUser()

    return token.user


@sync_to_async
def _user_belongs_to_organization(user, organization_id: str):
    """Check if user is a member of the given organization."""
    from mayan.apps.organizations.models import UserOrganizationRole
    return UserOrganizationRole.objects.filter(
        user=user,
        organization_id=organization_id,
    ).exists()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications (Phase 4). Tenant-scoped by organization_id."""

    async def connect(self):
        token = None
        organization_id = None
        try:
            query = parse_qs(self.scope.get('query_string', b'').decode('utf-8'))
            token = (query.get('token') or [None])[0]
            organization_id = (query.get('organization_id') or [None])[0]
        except Exception:
            token = None
            organization_id = None

        user = AnonymousUser()
        if token:
            user = await _get_user_from_token(token_string=token)

        if not getattr(user, 'is_authenticated', False):
            await self.close()
            return

        if not organization_id:
            await self.close(code=WS_CLOSE_ORG_DENIED)
            return

        belongs = await _user_belongs_to_organization(user, organization_id)
        if not belongs:
            await self.close(code=WS_CLOSE_ORG_DENIED)
            return

        self.user = user
        self.group_name = 'notifications_{}_{}'.format(organization_id, self.user.pk)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception:
            return

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except Exception:
            return

        if payload.get('type') == 'ping':
            await self.send(
                text_data=json.dumps(
                    {
                        'type': 'pong',
                        'timestamp': payload.get('timestamp'),
                    }
                )
            )

    async def notification_new(self, event):
        """Send a new notification payload to the client."""

        await self.send(text_data=json.dumps({'type': 'notification.new', 'data': event.get('data', {})}))
