from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('chat/', views.chat, name='chat'),
    path('logout/', views.logout_view, name='logout'),
]
