from django.contrib import admin
from .models import CustomUser, ChatHistory  # Importa os modelos necessários
from .models import Categoria, CategoriaLang, Especialidade, MatrizPadraoAtividade, CicloPadrao, Criticidade, ChaveModelo


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


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('cod_categoria', 'cod_categoria_pai')
    search_fields = ('cod_categoria',)
    list_filter = ('cod_categoria_pai',)

@admin.register(CategoriaLang)
class CategoriaLangAdmin(admin.ModelAdmin):
    list_display = ('cod_categoria', 'cod_idioma', 'descricao')
    search_fields = ('descricao',)
    list_filter = ('cod_idioma',)

@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ('cod_especialidade', 'descricao')
    search_fields = ('descricao',)

@admin.register(MatrizPadraoAtividade)
class MatrizPadraoAtividadeAdmin(admin.ModelAdmin):
    list_display = ('cod_categoria', 'cod_especialidade')
    list_filter = ('cod_categoria', 'cod_especialidade')

@admin.register(CicloPadrao)
class CicloPadraoAdmin(admin.ModelAdmin):
    list_display = ('cod_ciclo', 'descricao', 'intervalo_dias')
    search_fields = ('descricao',)

@admin.register(Criticidade)
class CriticidadeAdmin(admin.ModelAdmin):
    list_display = ('cod_criticidade', 'descricao', 'nivel')
    search_fields = ('descricao',)
    list_filter = ('nivel',)

@admin.register(ChaveModelo)
class ChaveModeloAdmin(admin.ModelAdmin):
    list_display = ('cod_chave', 'descricao')
    search_fields = ('descricao',)