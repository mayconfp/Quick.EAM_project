from django.urls import path
from . import views
from .views import password_reset_request, password_reset_confirm, validate_reset_code, alterar_status_especialidade
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
    path('definir-idioma/', views.definir_idioma, name="definir_idioma"),

 # 🔹 Rotas do GPP - Matriz Padrão Atividades
   path('gpp/categorias/', views.listar_categorias, name="listar_categorias"),
    path('gpp/categorias/nova/', views.criar_categoria, name="criar_categoria"),
    path('gpp/categorias/editar/<str:cod_categoria>/', views.editar_categoria, name="editar_categoria"),
    path('gpp/categorias/excluir/<str:cod_categoria>/', views.excluir_categoria, name="excluir_categoria"),
    path('gpp/categorias/adicionar_traducao/<str:cod_categoria>/', views.adicionar_traducao, name="adicionar_traducao"),

    # 🔹 Gerenciamento de Especialidades (GPP)
    path('gpp/especialidades/', views.listar_especialidades, name='listar_especialidades'),
    path('gpp/especialidades/nova/', views.criar_especialidade, name='criar_especialidade'),
    path('gpp/especialidades/editar/<str:cod_especialidade>/', views.editar_especialidade, name='editar_especialidade'),
    path('especialidades/status/<str:id>/', alterar_status_especialidade, name='alterar_status_especialidade'),


    # 🔹 Gerenciamento de Ciclos de Manutenção (GPP)
    path('gpp/ciclos/', views.listar_ciclos, name='listar_ciclos'),
    path('gpp/ciclos/criar/', views.criar_ciclo, name='criar_ciclo'),
    path('ciclos/editar/<str:cod_ciclo>/', views.editar_ciclo, name='editar_ciclo'),
    path('gpp/ciclos/excluir/<str:cod_ciclo>/', views.excluir_ciclo, name='excluir_ciclo'),

    # 🔹 Gerenciamento de Matriz Padrão Atividades (GPP)
    path('gpp/matriz/', views.listar_matriz, name='listar_matriz'),
    path('gpp/matriz/nova/', views.criar_matriz, name='criar_matriz'),
    path('gpp/matriz/editar/<str:id>/', views.editar_matriz, name='editar_matriz'),
    path('gpp/matriz/excluir/<str:id>/', views.excluir_matriz, name='excluir_matriz'),
]