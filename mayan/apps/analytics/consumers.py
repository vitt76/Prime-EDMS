from urllib.parse import parse_qs

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class AnalyticsDashboardConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for analytics dashboard refresh notifications."""

    group_name = None

    async def connect(self):
        user = self.scope.get('user')
        if not user or getattr(user, 'is_anonymous', True):
            await self.close()
            return

        # Multi-tenancy: organization_id must be provided for non-admin users.
        raw_qs = (self.scope.get('query_string') or b'').decode('utf-8', errors='ignore')
        parsed = parse_qs(raw_qs)
        organization_id = (
            (parsed.get('organization_id') or parsed.get('org_id') or parsed.get('org') or parsed.get('tenant') or [''])[0]
        ).strip()

        is_admin = bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))
        if not organization_id:
            if not is_admin:
                await self.close(code=4400)
                return
            # Admin broadcast group (can see all).
            self.group_name = 'analytics_dashboard_all'
        else:
            self.group_name = f'analytics_dashboard_{organization_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json(
            {
                'type': 'connected',
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


