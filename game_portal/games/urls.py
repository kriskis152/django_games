from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/<slug:slug>/', views.play_game, name='play_game'),
    path('upload/', views.upload_game, name='upload_game'),
    path('api/score/<int:game_id>/', views.submit_score, name='submit_score'),
]
