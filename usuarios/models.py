from django.conf import settings
from django.db import models


from django.db import models
from django.conf import settings


from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Adicione campos personalizados aqui, se necessário
    pass


class ChatHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True  # Certifique-se de que há uma vírgula no final da linha anterior
    )
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.question[:20]}"
