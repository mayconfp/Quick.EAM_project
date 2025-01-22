from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('deletar-conta/', views.deletar_conta, name='deletar_conta'),
    path('chat/', views.chat, name='chat'),
    path('chat/nova/', views.nova_conversa, name='nova_conversa'),
    path('chat/deletar/<int:session_id>/', views.deletar_conversa, name='deletar_conversa'),
    path('chat/excluir/<int:session_id>/', views.excluir_chat, name='excluir_chat'),
]

