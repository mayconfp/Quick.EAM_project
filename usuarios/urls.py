from django.urls import path
from . import views
from .views import password_reset_request, password_reset_confirm, validate_reset_code
from django.contrib.auth import views as auth_views

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
    path("password_reset/", password_reset_request, name="password_reset_request"),
    path("validate_reset_code/", validate_reset_code, name="validate_reset_code"),
    path("password_reset_confirm/", password_reset_confirm, name="password_reset_confirm"),
        

]