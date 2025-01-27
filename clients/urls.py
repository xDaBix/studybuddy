
from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('',views.home,name="home"),
    path('login/',views.login,name="login"),
    path('logout/',views.logout_view,name="logout"),
    path('signup/',views.signup,name="signup"),
    path('verifyotp/',views.verifyotp,name="verifyotp"),
    path('createroom/',views.createroom,name="createroom"),
    


    
]
