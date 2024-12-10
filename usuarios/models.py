from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    """Modelo de usuário personalizado."""
    pass

class ChatHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question[:50]}"
