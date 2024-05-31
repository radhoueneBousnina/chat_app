from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<int:user_id>/', views.get_or_create_room, name='get_or_create_room'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
]
