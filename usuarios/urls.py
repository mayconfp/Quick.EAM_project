from django.urls import path
from . import views
from .views import password_reset_request, password_reset_confirm, validate_reset_code


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
    path("password_reset/", password_reset_request, name="password_reset_request"),
    path("validate_reset_code/", validate_reset_code, name="validate_reset_code"),
    path("password_reset_confirm/", password_reset_confirm, name="password_reset_confirm"),
        
    
# 🔹 Rotas do GPP - Matriz Padrão Atividades
   path('gpp/categorias/', views.listar_categorias, name="listar_categorias"),
    path('gpp/categorias/nova/', views.criar_categoria, name="criar_categoria"),
    path('gpp/categorias/editar/<str:cod_categoria>/', views.editar_categoria, name="editar_categoria"),
    path('gpp/categorias/excluir/<str:cod_categoria>/', views.excluir_categoria, name="excluir_categoria"),
    path('gpp/categorias/adicionar_traducao/<str:cod_categoria>/', views.adicionar_traducao, name="adicionar_traducao"),

    # 🔹 Gerenciamento de Especialidades (GPP)
    path('gpp/especialidades/', views.lista_especialidades, name='lista_especialidades'),
    path('gpp/especialidades/nova/', views.criar_especialidade, name='criar_especialidade'),
    path('gpp/especialidades/editar/<str:cod_especialidade>/', views.editar_especialidade, name='editar_especialidade'),
    path('gpp/especialidades/excluir/<str:cod_especialidade>/', views.excluir_especialidade, name='excluir_especialidade'),

    # 🔹 Gerenciamento de Ciclos de Manutenção (GPP)
    path('gpp/ciclos/', views.lista_ciclos, name='lista_ciclos'),
    path('gpp/ciclos/novo/', views.criar_ciclo, name='criar_ciclo'),
    path('gpp/ciclos/editar/<str:id>/', views.editar_ciclo, name='editar_ciclo'),
    path('gpp/ciclos/excluir/<str:id>/', views.excluir_ciclo, name='excluir_ciclo'),

    # 🔹 Gerenciamento de Matriz Padrão Atividades (GPP)
    path('gpp/matriz/', views.lista_matriz_padrao, name='lista_matriz_padrao'),
    path('gpp/matriz/nova/', views.criar_matriz_padrao, name='criar_matriz_padrao'),
    path('gpp/matriz/editar/<int:id>/', views.editar_matriz_padrao, name='editar_matriz_padrao'),
    path('gpp/matriz/excluir/<int:id>/', views.excluir_matriz_padrao, name='excluir_matriz_padrao'),
]