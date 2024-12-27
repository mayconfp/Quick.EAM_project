from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:session_id>/', views.chat, name='chat_session'),
    path('chat/', views.chat, name='chat'),  # Rota para novo chat
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
]
