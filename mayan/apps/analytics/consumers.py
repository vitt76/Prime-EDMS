from channels.generic.websocket import AsyncJsonWebsocketConsumer


class AnalyticsDashboardConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for analytics dashboard refresh notifications."""

    group_name = 'analytics_dashboard_default'

    async def connect(self):
        user = self.scope.get('user')
        if not user or getattr(user, 'is_anonymous', True):
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({'type': 'connected', 'group': self.group_name})

    async def disconnect(self, code):
        try:
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
            }
        )


