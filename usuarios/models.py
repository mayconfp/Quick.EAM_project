import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


def user_profile_picture_path(instance, filename):
    """
    Renomeia os arquivos de imagem para evitar nomes longos.
    Exemplo: 'profile_pics/user_1_20250122.webp'
    """
    ext = filename.split('.')[-1]  # Obtém a extensão do arquivo
    filename = f"user_{instance.id}_{now().strftime('%Y%m%d')}.{ext}"  # Novo nome
    return os.path.join('profile_pics/', filename)



class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, null=True, blank=True, max_length=255)

    def __str__(self):
        return self.username


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


