from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, MessageForm, UserForm, MyUserCreationForm

# Create your views here.


def login_page(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        else:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                return redirect('home')
            else:
                messages.error(request, 'Username or Password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context=context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_page(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')

    context = {'page': page,
               'form': form}
    return render(request, 'base/login_register.html', context=context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()

    rooms_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms,
               'topics': topics,
               'rooms_count': rooms_count,
               'room_messages': room_messages,
               }
    return render(request, 'base/home.html', context=context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()

    messagers = [message.user for message in room_messages]
    for participant in room.participants.all():
        if participant not in messagers:
            room.participants.remove(participant)

    room.save()

    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get('body'))
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room,
               'room_messages': room_messages,
               'participants': participants,
               }

    return render(request, 'base/room.html', context=context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()  # get all the children rooms linked to the user
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user,
               'rooms': rooms,
               'room_messages': room_messages,
               'topics': topics,
               }
    return render(request, 'base/user_profile.html', context=context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic').title()
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('room_name'),
            description=request.POST.get('description'),
        )

        return redirect('home')

    context = {'form': form,
               'topics': topics}

    return render(request, 'base/room_form.html', context=context)


@login_required(login_url='login')
def update_room(request, pk):
    url_p = request.path
    url_p = url_p.split('/')[1]

    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('you are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic').title()
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('room_name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form,
               'topics': topics,
               'room': room,
               'url_p': url_p
               }
    return render(request, 'base/room_form.html', context=context)


@login_required(login_url='login')
def update_message(request, pk):
    room_message = Message.objects.get(id=pk)
    form = MessageForm(instance=room_message)

    if request.user != room_message.user:
        return HttpResponse('you are not allowed here!!')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=room_message)
        if form.is_valid():
            form.save()
            room = room_message.room
            return redirect('room', pk=room.id)

    context = {'form': form}
    return render(request, 'base/room_message_form.html', context=context)


@login_required(login_url='login')
def delete_message(request, pk):
    room_message = Message.objects.get(id=pk)
    print(room_message)

    if request.user != room_message.user:
        return HttpResponse('you are not allowed here!!')

    if request.method == 'POST':
        room = room_message.room
        room_message.delete()
        return redirect('room', pk=room.id)

    return render(request, 'base/delete.html', context={'obj': room_message})


@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('you are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', context={'obj': room})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form, }
    return render(request, 'base/edit-user.html', context=context)


@login_required(login_url='login')
def settings(request):
    context = {}
    return render(request, 'base/settings.html', context=context)
