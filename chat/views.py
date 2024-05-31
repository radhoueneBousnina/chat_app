from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Room

User = get_user_model()


@login_required(login_url='accounts:login')
def index(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'index.html', {'users': users})


@login_required(login_url='accounts:login')
def chat_room(request, room_id):
    first_name = request.session.get('first_name')
    last_name = request.session.get('last_name')
    return render(request, 'chat/chat_room.html', {'room_id': room_id, 'first_name': first_name, 'last_name': last_name})


@login_required(login_url='accounts:login')
def get_or_create_room(request, user_id):
    other_user = User.objects.get(id=user_id)
    room = Room.objects.filter(participants=request.user).filter(participants=other_user).distinct().first()
    if not room:
        room = Room.objects.create()
        room.participants.add(request.user, other_user)
    request.session['first_name'] = other_user.first_name
    request.session['last_name'] = other_user.last_name
    return redirect('chat:chat_room', room_id=room.id)
