import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ShopConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('chat', self.channel_name)
        try:
            print(f"[ws] connect: channel={self.channel_name} path={self.scope.get('path')}")
        except Exception:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data.get('action')

        try:
            print(f"[ws] receive: channel={self.channel_name} action={action} data={data}")
        except Exception:
            pass

        if action == 'join_order':
            order_id = data.get('order_id')
            group = f'order_{order_id}'
            await self.channel_layer.group_add(group, self.channel_name)
            await self.send(json.dumps({'joined': order_id}))
        elif action == 'chat':
            msg = data.get('message')
            await self.channel_layer.group_send('chat', {'type': 'chat.message', 'message': msg})

    async def order_update(self, event):
        try:
            print(f"[ws] order_update event={event}")
        except Exception:
            pass
        await self.send(json.dumps({'type': 'order_update', 'order_id': event.get('order_id'), 'status': event.get('status')}))

    async def chat_message(self, event):
        try:
            print(f"[ws] chat_message event={event}")
        except Exception:
            pass
        await self.send(json.dumps({'type': 'chat', 'message': event.get('message')}))

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard('chat', self.channel_name)
        except Exception:
            pass
        try:
            print(f"[ws] disconnect: channel={self.channel_name} code={close_code}")
        except Exception:
            pass
