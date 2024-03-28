import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from .models import GameChat, GameUsers, UserGames
from users.models import User
from channels.db import database_sync_to_async

class GameChatRoomConsumer(AsyncWebsocketConsumer):   
    @database_sync_to_async 
    def get_all_chats(self, game_id):
        all = list(GameChat.objects.filter(game_id=game_id).values())
        return all
    
    @database_sync_to_async
    def save_message(self, user_id, game_id, message):
        user = User.objects.get(id=user_id)
        game = UserGames.objects.get(id=game_id)
        
        game_message = GameChat.objects.create(user_id=user, game_id=game, message=message)
        game_message.save()
        
        data = {
            'id' : game_message.id,
            'user_id' : user_id,
            'game_id' : game_id,
            'message' : message,
            'date_time' : game_message.date_time.isoformat(),
            'user' : {
                'id' : user.id,
                'email' : user.email,
                'phone' : user.phone,
                'player_username' : user.player_username,
                'skill_level' : user.skill_level 
            } 
        }        
        
        if user.profile_img:
            data['user']['profile_img'] = user.profile_img.url
        else:
            data['user']['profile_img'] = None
        
        return data
    
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()        
        
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        user_id = text_data_json['user_id']
        game_id = text_data_json['game_id']
        message = text_data_json["message"]
        
        chat_message = await self.save_message(user_id, game_id, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": chat_message}
        )
        
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
        
        
    
        