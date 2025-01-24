from django.urls import path
from . import views
from .views import password_reset_request, password_reset_confirm
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('chat/<int:session_id>/', views.chat, name='chat_session'),
    path('chat/', views.chat, name='chat'),
    path('nova-conversa/', views.nova_conversa, name='nova_conversa'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('deletar_conversa/<int:session_id>/', views.deletar_conversa, name='deletar_conversa'),
    path('perfil/', views.perfil, name='perfil'),
    path('deletar_conta/', views.deletar_conta, name='deletar_conta'),

    path("password_reset/", views.password_reset_request, name="password_reset_request"),
    # URL para página de sucesso após solicitação
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(template_name="usuarios/password_reset_done.html"), name="password_reset_done"),

    # URL para redefinição da senha (quando o usuário clica no link do e-mail)
   path("reset_password/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="usuarios/password_reset_confirm.html"), name="password_reset_confirm"),




    # URL para página de sucesso após redefinir a senha
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="usuarios/password_reset_complete.html"), name="password_reset_complete"),
        
]
