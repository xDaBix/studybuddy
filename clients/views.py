from datetime import datetime, timedelta, timezone
import random
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render , get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import registration,Room,Messages
from .forms import regform,roomform,createroomform
from django.contrib.auth.hashers import make_password, check_password


def signup(request):
    if request.session.get("id"):
        return redirect('home')
            
    if request.method == "POST":
        form = regform(request.POST)
        if form.is_valid():
            fname = form.cleaned_data.get('firstname')
            lname = form.cleaned_data.get('lastname')
            con = form.cleaned_data.get('contactno')
            gender = form.cleaned_data.get('gender')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')  
            dob = form.cleaned_data.get('dateofbirth')
            
            if registration.objects.filter(email=email).exists():
                messages.error(request, 'Email is already registered')
                return render(request, "clients/signup.html", {"form": form})

            otp = random.randint(10000, 99999)
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )

            form.cleaned_data['dateofbirth'] = dob.strftime('%Y-%m-%d')
            form.cleaned_data['otp'] = otp
            request.session['regdata'] = form.cleaned_data
            request.session.modified = True
            return redirect('verifyotp')
        
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = regform()

    return render(request, "clients/signup.html", {"form": form})


def login(request):
    if request.session.get("id"):
        return redirect('home')
    
    client1 = None
    attempts_left = 3

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            client1 = registration.objects.get(email=email)
        except registration.DoesNotExist:
            client1 = None

        if client1:
            if client1.lockout_time and timezone.now() >= client1.lockout_time:
                client1.lockout_time = None
                client1.failed_attempts = 0
                client1.save()

            if client1.lockout_time and timezone.now() < client1.lockout_time:
                messages.error(request, 'Your account is locked. Try again later.')
                return render(request, 'clients/login.html', {'attempts_left': 0})

            if check_password(password, client1.password):
                client1.failed_attempts = 0
                client1.lockout_time = None
                client1.save()
                request.session['id'] = client1.clientid
                request.session.modified = True
                messages.success(request, "Login successful")
                return redirect('home')
            else:
                client1.failed_attempts += 1

                if client1.failed_attempts >= 3:
                    client1.lockout_time = timezone.now() + timedelta(minutes=15)
                    messages.error(request, 'You have made 3 incorrect attempts. Your account is locked for 15 minutes.')
                else:
                    remaining_attempts = 3 - client1.failed_attempts
                    messages.error(request, f'Invalid email or password. Attempts left: {remaining_attempts}')

                client1.save()
        else:
            messages.error(request, 'Invalid email or password.')

    attempts_left = 3 if not client1 else max(0, 3 - client1.failed_attempts)

    return render(request, 'clients/login.html', {'attempts_left': attempts_left})

def home(request):
    q = request.GET.get('q')
    
    if not request.session.get("id"):
        return redirect('login') 

    topics = Room.objects.values_list('topics', flat=True).distinct()
    croom = Room.objects.filter(clientid=request.session.get("id"))
    all_rooms = Room.objects.all()  
    
    context = {
        'topics': topics,
        'rooms': croom,
        'all_rooms': all_rooms  
    }
    
    return render(request, "clients/home.html", context)


def verifyotp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        regdata = request.session.get('regdata')
        
        if not regdata:
        
            messages.error(request, 'Session data missing. Please try again.')
            return redirect('signup')  
        
        
        if otp and int(otp) == regdata.get('otp'):
            try:
                dobstr = regdata.get('dateofbirth')
                dob1 = datetime.strptime(dobstr, '%Y-%m-%d').date()
                
                
                cl = registration(
                    firstname=regdata.get('firstname'),
                    lastname=regdata.get('lastname'),
                    contactno=regdata.get('contactno'),
                    gender=regdata.get('gender'),
                    email=regdata.get('email'),
                    password=make_password(regdata.get('password')),
                    dateofbirth=dob1
                )
                cl.save()

                
                request.session['id'] = cl.clientid
                request.session.modified = True
                messages.success(request, 'Registration successful')
                return redirect('home')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('signup') 
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('verifyotp')  

    return render(request, 'clients/verifyotp.html')


def logout_view(request):
    logout(request)
    return redirect('login')

def create_room(request):
    return render(request, 'clients/room.html')

def createroom(request):
    if request.method == "POST":
        room_name = request.POST.get("name")
        room_description = request.POST.get("description")
        
        if room_name and room_description:
            room = Room(name=room_name, description=room_description)
            room.save()
            messages.success(request, 'Room created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please fill in all fields.')
            return redirect('create_room')

def roomdetail(request, id):
    if not request.session.get("id"):
        return redirect('login')

    room = get_object_or_404(Room, roomid=id)
    user = get_object_or_404(registration, clientid=request.session.get("id"))

    is_owner = room.clientid == request.session.get("id")
    is_participant = room.participants.filter(clientid=request.session.get("id")).exists()

    messages = Messages.objects.filter(room=room).order_by("createdtime")
    participants = room.participants.all()

    if request.method == "POST":
        body = request.POST.get("message", "").strip()
        if body:
            Messages.objects.create(clientid=user, room=room, body=body)

    return render(request, "clients/roomdetail.html", {
        "room": room,
        "messages": messages,
        "participants": participants,
        "is_participant": is_participant,
        "is_owner": is_owner
    })

def room_messages(request, room_id):
    user_id = request.session.get("id")
    if not user_id:
        return redirect('login')

    user = get_object_or_404(registration, clientid=user_id)
    room = get_object_or_404(Room, roomid=room_id)

    is_owner = room.clientid == user
    is_participant = room.participants.filter(clientid=user).exists()

    if not (is_owner or is_participant):
        return redirect('home')

    if request.method == "POST":
        body = request.POST.get("message")
        if body:
            Messages.objects.create(clientid=user, room=room, body=body)

    messages = Messages.objects.filter(room=room).order_by("createdtime")

    context = {
        "room": room,
        "messages": messages,
        "is_participant": is_participant,
        "is_owner": is_owner
    }
    
    return render(request, "clients/roomdetail.html", context)

def join_room(request, roomid):
    room = get_object_or_404(Room, roomid=roomid)
    if room.owner != request.user:
        room.members.add(request.user)
        return redirect('roomdetail', roomid=roomid)
    else:
        return redirect('home')