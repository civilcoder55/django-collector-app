from channels.generic.websocket import AsyncJsonWebsocketConsumer


class PostConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        if not self.scope['user'].is_anonymous:
            await self.channel_layer.group_add("notifier", self.channel_name)
            print(f"Added {self.channel_name} channel to notifier")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifier", self.channel_name)
        print(f"Removed {self.channel_name} channel to notifier")

    async def send_notification(self, event):
        await self.send_json({
            'id': event['id'],
            'title': event['title'],
            'thumnail_photo': event['thumnail_photo']
        })
