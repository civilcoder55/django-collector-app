from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        if not self.scope['user'].is_anonymous:
            await self.channel_layer.group_add("notifier", self.channel_name)
            await self.accept()
            print(f"Added {self.channel_name} channel to notifier")

    async def disconnect(self,status_code):
        await self.channel_layer.group_discard("notifier", self.channel_name)
        print(f"Removed {self.channel_name} channel to notifier")

    async def send_notification(self, event):
        await self.send_json({
            "event": event
        })
