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

    # 🔹 Rotas do GPP - Categorias
    path('gpp/categorias/', views.lista_categorias, name='lista_categorias'),
    path('gpp/categorias/nova/', views.criar_categoria, name='criar_categoria'),
    path('gpp/categorias/editar/<str:cod_categoria>/', views.editar_categoria, name='editar_categoria'),
    path('gpp/categorias/excluir/<str:cod_categoria>/', views.excluir_categoria, name='excluir_categoria'),

    # 🔹 Rotas do GPP - Especialidades
    path('gpp/especialidades/', views.lista_especialidades, name='lista_especialidades'),
    path('gpp/especialidades/nova/', views.criar_especialidade, name='criar_especialidade'),
    path('gpp/especialidades/editar/<str:cod_especialidade>/', views.editar_especialidade, name='editar_especialidade'),
    path('gpp/especialidades/excluir/<str:cod_especialidade>/', views.excluir_especialidade,
         name='excluir_especialidade'),

    # 🔹 Rotas do GPP - Ciclos de Manutenção
    path('gpp/ciclos/', views.lista_ciclos, name='lista_ciclos'),
    path('gpp/ciclos/novo/', views.criar_ciclo, name='criar_ciclo'),
    path('gpp/ciclos/editar/<str:cod_ciclo>/', views.editar_ciclo, name='editar_ciclo'),
    path('gpp/ciclos/excluir/<str:cod_ciclo>/', views.excluir_ciclo, name='excluir_ciclo'),
]