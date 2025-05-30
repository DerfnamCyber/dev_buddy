from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.contrib.auth.models import User

#<a href="{{ request.META.HTTP_REFERER}}">      Sends the user back to the previous page

def loginPage(request):
    page = 'login'
    
    if request.user.is_authenticated:   #Prevent the user from re-login 
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:    #Used here to check if the user exist
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
         
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password does not exist')
    
    context = {
            'page' : page
        
    }
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)     #delete tha token
    return redirect('home')

#Register will be underneath logout

def registerPage(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  #Saving the form to access the user right away
            user.username = user.username.lower()   #converting to lower~cleaned
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    context = {
        'form' : form
    }
    return render(request, 'base/login_register.html', context)
    
def home(request):
    #queryset = ModelName.objects.all(), {    .get(), .filter(), .exclude()   }
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
        ) #Check if it contains the search item---"i" makes it case insensitive
    
    topics = Topic.objects.all()[0:5]   #displays the first five topics
    room_count = rooms.count()       #length of a queryset(i.e rooms available)
    room_messages = Message.objects.all().filter(Q(room__topic__name__icontains=q))
    
    context = {
        'rooms' : rooms,
        'topics' : topics,
        'room_count' : room_count,
        'room_messages' : room_messages
    }
    return render(request, 'base/home.html', context)



def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')  #Giving set of messages related to the room, a query
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)     #Add a user and render the user information out
        return redirect('room', pk=room.id) #Redirect the user back to the room page
    
    context = {
        'room' : room,
        'participants' : participants,
        'room_messages' : room_messages,
    }
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() #get all this users rooms(Get all the children)
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={
        'user':user,
        'rooms' : rooms,
        'room_messages' : room_messages,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')    #Where we want to redirect the user
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    
    if request.method == "POST":
        #request.POST.get('name')
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'), 
            description=request.POST.get('description'), 
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     # form.save()
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')

    context = {
        'form' : form,
        'topics':topics
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login') 
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)       #Creates an instance that pre fills the form
    topics = Topic.objects.all()
    
    if request.user != room.host:       #Ensures only the required user is able tp update the room
        return HttpResponse("<h1>You are not allowed here!</h1>")
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.name = request.POST.get('name')
        room.name = request.POST.get('name')
        return redirect('home')
        
        #form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={
        'form' : form,
        'topics' :topics,
        'room' : room
    }
    return render(request, 'base/room_form.html', context)    


@login_required(login_url='login') 
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:       #Ensures only the required user is able tp update the room
        return HttpResponse("<h1>You are not allowed here!</h1>")
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {
        'obj' : room
    }
    return render(request, 'base/delete.html', context)

@login_required(login_url='login') 
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:       #Ensures only the required user is able tp update the room
        return HttpResponse("<h1>You are not allowed here!</h1>")
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {
        'obj' : message
    }
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance = user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance = user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
        
    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
   
    context = {
        'topics' : topics,
    }
    return render(request, 'base/topics.html',context)

def activityPage(request):
    room_messages = Message.objects.filter()[0:4]
    context = {
        'room_messages' : room_messages
    }
    return render(request, 'base/activity.html', context)

