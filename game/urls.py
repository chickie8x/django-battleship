from django.urls import path
from . import views

urlpatterns = [
    path('',views.index_view,name="index"),
    path('gameid/<str:gameid>', views.game_view, name='game'),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("creategame", views.create_game, name="creategame"),
    path('playgame', views.play_game, name='playgame'),
    path('matchmaking',views.matchmaking, name='matchmaking'),
]