from django.contrib import admin
from .models import CustomUser

# Registro do modelo no painel de administração
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
