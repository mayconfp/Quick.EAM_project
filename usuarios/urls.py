from django.urls import path
from . import views
from .views import editar_titulo

urlpatterns = [
    path('chat/<int:session_id>/', views.chat, name='chat_session'),
    path('chat/', views.chat, name='chat'),
    path('chat/excluir/<int:session_id>/', views.excluir_chat, name='excluir_chat'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('chat/<int:session_id>/editar_titulo/', editar_titulo, name='editar_titulo'),
    path('perfil/', views.perfil, name='perfil_usuario'),
    path('deletar_conta/', views.deletar_conta, name='deletar_conta'),



]

