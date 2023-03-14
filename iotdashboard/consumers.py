from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json


class RealTimeConsumer(WebsocketConsumer):
    print('test')
    def connect(self):
        print('Connecting')
        self.accept()
        self.send(text_data="Return message from backend")
    
    def disconnect(self, code):
        print("Connection is disconnected")

class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("users", self.channel_name)

        await self.channel_layer.group_send(
			'users',
			{
				"type": "user_update",
				"event": "Change Status",
			}
		)
        # self.id = self.scope['url_route']['kwargs']['id']
        # print(self.id)

        # await self.channel_layer.group_add(
        #     self.id,
        #     self.channel_name
        # )


    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.id,
            self.channel_name
        )
        await self.close()
    
    async def update_params(self, event):
        await self.send(text_data=json.dumps(event['text']))