from channels.generic.websocket import AsyncJsonWebsocketConsumer


class PostConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        if not self.scope['user'].is_anonymous:
            await self.channel_layer.group_add("posts", self.channel_name)
            print(f"Added {self.channel_name} channel to posts")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("posts", self.channel_name)
        print(f"Removed {self.channel_name} channel to posts")

    async def send_notification(self, event):
        message = {
            'post_id': event['post_id'],
            'thumnail_photo': event['thumnail_photo'],
            'title': event['title'],
            'link': event['link'], }
        await self.send_json(message)
