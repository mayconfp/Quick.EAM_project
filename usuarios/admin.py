from django.contrib import admin
from .models import CustomUser, ChatHistory,Especialidade  # Importa os modelos necessários

# Registro do modelo CustomUser no admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')  # Campos exibidos no admin
    search_fields = ('username', 'email')  # Campos para pesquisa

# Registro do modelo ChatHistory no admin
@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'timestamp')  # Colunas exibidas no admin
    search_fields = ('question', 'answer', 'user__username')   # Campos para pesquisa
    list_filter = ('timestamp',)                              # Filtros por data

@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ('cod_especialidade', 'descricao', 'ativo', 'responsavel', 'data_criacao', 'data_atualizacao')
    list_filter = ('ativo', 'responsavel', 'data_criacao')
    search_fields = ('cod_especialidade', 'descricao')
