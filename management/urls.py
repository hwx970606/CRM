from django.contrib import admin
from django.urls import path,include
from stark.service.stark import site
from management.views import account

urlpatterns = [
    path('login/',account.login,name='login'),
    path('logout/',account.logout,name='logout'),
    path('index/',account.index,name='index')
]