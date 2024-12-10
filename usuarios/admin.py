from django.contrib import admin
from .models import CustomUser, ChatHistory  # Importa os modelos necessários
from usuarios.models import ChatHistory, CustomUser

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
