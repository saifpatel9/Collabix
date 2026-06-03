import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.reports.services.analytics_service import AnalyticsService


class AnalyticsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        self.group_name = f"analytics-{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.push_kpis()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        action = content.get("action", "refresh")
        if action == "refresh":
            await self.push_kpis()

    async def analytics_update(self, event):
        await self.send_json(event["payload"])

    async def push_kpis(self):
        kpis = await self._get_kpis()
        await self.send_json({"type": "kpi_update", "payload": kpis})

    async def chart_update(self, event):
        await self.send_json({"type": "chart_update", "chart": event["chart"], "payload": event["payload"]})

    @database_sync_to_async
    def _get_kpis(self):
        svc = AnalyticsService()
        return svc.kpi_dashboard(self.user)
