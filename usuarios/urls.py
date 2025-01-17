from django.urls import path
from . import views

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

]
