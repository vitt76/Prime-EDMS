from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


WS_CLOSE_BAD_REQUEST = 4400
WS_CLOSE_ORG_DENIED = 4003


@sync_to_async
def _get_user_from_token(token_string: str):
    """Resolve DRF token key into a Django user for SPA websocket auth."""
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
    from mayan.apps.organizations.models import UserOrganizationRole

    return UserOrganizationRole.objects.filter(
        user=user,
        organization_id=organization_id,
    ).exists()


class AnalyticsDashboardConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for analytics dashboard refresh notifications."""

    group_name = None

    async def connect(self):
        raw_qs = (
            self.scope.get('query_string') or b''
        ).decode('utf-8', errors='ignore')
        parsed = parse_qs(raw_qs)
        token = (parsed.get('token') or [''])[0].strip()
        organization_id = ''
        for key in ('organization_id', 'org_id', 'org', 'tenant'):
            values = parsed.get(key) or []
            if values and values[0].strip():
                organization_id = values[0].strip()
                break

        user = self.scope.get('user')
        if (not user or getattr(user, 'is_anonymous', True)) and token:
            user = await _get_user_from_token(token_string=token)

        if not user or getattr(user, 'is_anonymous', True):
            await self.close()
            return

        is_admin = bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))
        if not organization_id:
            if not is_admin:
                await self.close(code=WS_CLOSE_BAD_REQUEST)
                return
            # Admin broadcast group (can see all).
            self.group_name = 'analytics_dashboard_all'
        else:
            if not is_admin:
                belongs = await _user_belongs_to_organization(
                    user=user,
                    organization_id=organization_id
                )
                if not belongs:
                    await self.close(code=WS_CLOSE_ORG_DENIED)
                    return
            self.group_name = f'analytics_dashboard_{organization_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json(
            {
                'type': 'analytics.connected',
                'group': self.group_name,
                'organization_id': organization_id or None,
                'is_admin': is_admin,
            }
        )

    async def disconnect(self, code):
        try:
            if self.group_name:
                await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception:
            pass

    async def analytics_refresh(self, event):
        await self.send_json(
            {
                'type': 'analytics_refresh',
                'reason': event.get('reason', ''),
                'timestamp': event.get('timestamp'),
                'dashboard': event.get('dashboard', ''),
                'asset_id': event.get('asset_id'),
                'metric': event.get('metric', ''),
                'value': event.get('value'),
                'payload': event.get('payload') or {},
                'organization_id': event.get('organization_id'),
            }
        )

