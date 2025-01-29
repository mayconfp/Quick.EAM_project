import os
import random
import string
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import timedelta

def user_profile_picture_path(instance, filename):
    """
    Renomeia os arquivos de imagem para evitar nomes longos.
    Exemplo: 'profile_pics/user_1_20250122.webp'
    """
    ext = filename.split('.')[-1]  # Obtém a extensão do arquivo
    filename = f"user_{instance.id}_{now().strftime('%Y%m%d')}.{ext}"  # Novo nome
    return os.path.join('profile_pics/', filename)



class CustomUser(AbstractUser):

    email = models.EmailField(
        unique= True,
        blank= False,
        null = False,
        help_text="Email Obrigatório."
    )

    cnpj = models.CharField(
        max_length=18, 
        blank=True, 
        null=True, 
        unique=True, 
        help_text="CNPJ do usuário (opcional)."
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        help_text="Foto do perfil do usuário."
    )


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )
    title = models.CharField(max_length=100, default="Nova Conversa")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class ChatHistory(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    question = models.TextField()
    answer = models.TextField()
    ia_used = models.CharField(
        max_length=50,
        choices=[
            ('GPT', 'GPT'),
            ('Llama', 'Llama'),
            ('Gemini', 'Gemini'),
        ],
        default='GPT'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user}: {self.question[:20]} - {self.ia_used}"



User = get_user_model()

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(default=now)  # 🔥 Usa o timezone do Django corretamente

    def generate_code(self):
        """Gera um código aleatório de 6 dígitos e atualiza o timestamp"""
        self.code = ''.join(random.choices(string.digits, k=6))
        self.created_at = now()  # 🔥 Atualiza o horário de criação corretamente
        self.save()

    def is_expired(self):
        """Verifica se o código expirou após 5 minutos"""
        expiration_time = self.created_at + timedelta(minutes=5)
        current_time = now()  # 🔥 Obtém o horário correto do Django
        is_expired = current_time > expiration_time

        print(f"📌 Verificando expiração do código: {self.code} "
              f"(Expira em {expiration_time}, Agora: {current_time}) -> Expirado? {is_expired}")

        return is_expired