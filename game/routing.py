from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/', consumers.LobbyConsumer.as_asgi()),
    path('ws/gameid/<str:gameid>/', consumers.GameConsumer.as_asgi()),
]