from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Adicione campos personalizados aqui, se necessário
    pass

class ChatHistory(models.Model):
    IA_CHOICES = [
        ('GPT', 'GPT'),
        ('Llama', 'Llama'),
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
        max_length=50,
        choices=IA_CHOICES,
        default='GPT'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.question[:20]} - {self.ia_used}"