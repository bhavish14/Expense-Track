from django.urls import path
from .views import *

urlpatterns = [
    path('signIn', sign_in, name='signIn'),
    path('signUp', sign_up, name='signUp'),
    path('logout', logout, name='logout'),

    
]   