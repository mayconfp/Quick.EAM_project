from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('chat/<int:session_id>/', views.chat, name='chat'),
    path('chat/', views.new_chat, name='new_chat'),
    path('set_language_by_location/', views.set_language_by_location, name='set_language_by_location'),
]
