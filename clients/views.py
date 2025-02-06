from datetime import datetime, timedelta, timezone
import random
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import registration,Room
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
    topics = Room.objects.values_list('topics',flat=True).distinct()
    croom=Room.objects.filter(clientid=request.session.get("id"))
    context = {'topics': topics,'rooms':croom}
    return render(request, "clients/home.html", context)



def verifyotp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        re = request.session.get('regdata')
        if otp and re and int(otp) == re.get('otp'):
            dobstr = re.get('dateofbirth')
            dob1 = datetime.strptime(dobstr, '%Y-%m-%d').date()
            cl = registration(
                firstname=re.get('firstname'),
                lastname=re.get('lastname'),
                contactno=re.get('contactno'),
                gender=re.get('gender'),
                email=re.get('email'),
                password=make_password(re.get('password')),
                dateofbirth=dob1
            )
            cl.save()
            request.session['id'] = cl.clientid
            request.session.modified = True
            messages.success(request, 'Registration successful')
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')
    return render(request, 'clients/verifyotp.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def createroom1(request):
    if not request.session.get("id"):
        return redirect('login')
    if request.method == "POST":
        form=createroomform(request.POST)
        if form.is_valid():
            name=request.POST.get('name')
            description=request.POST.get('description')
            client_id = request.session.get("id")
            client_instance = registration.objects.get(clientid=client_id)
            room1=Room(name=name,roomdescription=description,clientid=client_instance)
            room1.save()
            messages.success(request, 'Room created successfully')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.') 
    else:
        form=createroomform()
    return render(request, "clients/room.html",{"form":form})


def roomdetail(request,id):
    if not request.session.get("id"):
        return redirect('login')
    room=Room.objects.get(roomid=id)
    return render(request, "clients/roomdetail.html",{"room":room})