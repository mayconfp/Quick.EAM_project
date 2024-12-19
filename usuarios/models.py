from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatHistory(models.Model):
    IA_CHOICES = [
        ('GPT', 'GPT'),
        ('LlAMA', 'LlAMA '),
        ('Gemini', 'Gemini'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    question = models.TextField()
    answer = models.TextField()
    ia_used = models.CharField(
        max_length=10,
        choices=IA_CHOICES,
        default='GPT'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey('ChatSession', on_delete=models.CASCADE, related_name='histories', null=True, blank=True)

    def __str__(self):
        return f"Usuário: {self.user}, IA: {self.ia_used}, Pergunta: {self.question[:20]}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
