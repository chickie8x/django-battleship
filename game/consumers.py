import json
import channels
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models.signals import post_save
from game.models import Game





class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_group_name = 'lobbies'

        await self.channel_layer.group_add(
            self.lobby_group_name,
            self.channel_name,
        )
        await self.accept()


    async def disconnect(self, code):
        self.lobby_group_name = 'lobbies'

        await self.channel_layer.group_discard(
            self.lobby_group_name,
            self.channel_name,
        )
    

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['gameid']
        # Send message to game group
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'create_event',
                'message': message
            }
        )

     # Receive message from game group
    async def create_event(self, event):
        message = event['message']
        ev_type='created'
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'ev_type':'created',
            'gameid': message,
        }))


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['gameid']
        self.game_group_name = 'game_%s' % self.game_id
        self.connected_user = self.scope['user']

        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )

        await self.accept()

        # player connected detection 
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'incoming_connection',
                'message': 'connected',
                'user': str(self.connected_user),
                'gameid': self.game_id,
                'userid':self.connected_user.id
            }
        )

    async def disconnect(self, close_code):
        self.game_id = self.scope['url_route']['kwargs']['gameid']
        self.game_group_name = 'game_%s' % self.game_id
        self.connected_user = self.scope['user']

        # player left game alert 
        # await self.player_leave()

        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'disconnected_player',
                'message':'left',
                'user': str(self.connected_user),
                'game': self.game_id

            }
        )

        # Leave game group
        await self.channel_layer.group_discard(
            self.game_id,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to game group
        if message == 'marked_cell':
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'marked_cell',
                    'cell_owner': text_data_json['cell_owner'],
                    'game': text_data_json['game'],
                    'index': text_data_json['index'],
                    'cell_status': text_data_json['cell_status'],
                    'message': text_data_json['message'],
                    'current_turn': text_data_json['current_turn']
                }
            )
        if message == 'end_game':
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'end_game',
                    'winner': text_data_json['final_winner']
                }
            )
        if message == 'chat':
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'chat',
                    'author': text_data_json['author'],
                    'chat_message': text_data_json['chat_message']
                }
            )

    # Receive message from game group

    #user connect to game 
    async def incoming_connection(self, event):
        message = event['message']
        user = event['user']
        game_id = event['gameid']
        user_id = event['userid']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user':user,
            'game': game_id,
            'userid':user_id
        }))

    #user disconnect from game 
    async def disconnected_player(self,event):
        message = event['message']
        user = event['user']
        game = event['game']

        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'game':game,
        }))

    #user mark a cell 
    async def marked_cell(self,event):
        cell_owner = event['cell_owner']
        game = event['game']
        index = event['index']
        message = event['message']
        cell_status = event['cell_status']
        current_turn_value = event['current_turn']

        await self.send(text_data=json.dumps({
            'cell_owner': cell_owner,
            'game': game,
            'index': index,
            'cell_status': cell_status,
            'message': message,
            'current_turn': current_turn_value,
        }))

    # game is finished
    async def end_game(self, event):
        message = 'end_game'
        winner = event['winner']
        await self.send(text_data=json.dumps({
            'message':message,
            'final_winner': winner
        }))

    # chat message
    async def chat(self,event):
        author = event['author']
        chat_message = event['chat_message']
        await self.send(text_data=json.dumps({
            'message': 'chat',
            'author': author,
            'chat_message': chat_message
        }))

    