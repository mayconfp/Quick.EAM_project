from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('chat/', views.chat, name='chat'),
    path('listar/', views.listar_usuarios, name='listar_usuarios'),
    path('logout/', views.logout_view, name='logout'),
]


