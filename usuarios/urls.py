from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('chat/', views.chat, name='chat'),
    path('set-language/', views.set_language_by_location, name='set_language_by_location'),
    path('logout/', views.logout_view, name='logout'),
]
