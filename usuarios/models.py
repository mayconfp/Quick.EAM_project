from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Adicione campos personalizados aqui, se necessário
    pass

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
        default='GPT'  # Define 'GPT' como padrão caso o campo não seja informado
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usuário: {self.user}, IA: {self.ia_used}, Pergunta: {self.question[:20]}"
