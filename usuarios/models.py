import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from .validators import validar_cnpj_existente  # Importa o validador que consulta a API
import re  # Para normalização do CNPJ
from django.contrib.auth import get_user_model
from datetime import timedelta
import random
import string


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
        max_length=220,
        blank=False,
        null=False,
        unique=True,
        help_text='E-mail obrigatório para cadastro'
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

    def save(self, *args, **kwargs):
        # Normaliza o CNPJ antes de salvar
        if self.cnpj:
            self.cnpj = re.sub(r'\D', '', self.cnpj)  # Remove . / -
        super().save(*args, **kwargs)



# Mantém as classes abaixo inalteradas
class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )
    title = models.CharField(max_length=100, default="Nova Conversa")
    created_at = models.DateTimeField(auto_now_add=True)

    contexto_usado = models.TextField(blank=True, null=True)

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
    file_url = models.URLField(blank=True, null=True)  # ✅ Campo para armazenar a URL do arquivo
    file_name = models.CharField(max_length=255, blank=True, null=True)  # ✅ Nome do arquivo
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





class Categoria(models.Model):
    cod_categoria = models.CharField(max_length=50, primary_key=True)
    cod_categoria_pai = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="subcategorias")
    descricao = models.CharField(max_length=255, null=True, blank=True)  # Nova coluna

    def __str__(self):
        return f"{self.cod_categoria} - {self.descricao if self.descricao else ''}"

class CategoriaLang(models.Model):
    cod_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="traducoes")
    cod_idioma = models.CharField(max_length=2)  # Exemplo: "en", "pt", "es"
    descricao = models.CharField(max_length=255)

    class Meta:
        unique_together = ('cod_categoria', 'cod_idioma')

    def __str__(self):
        return f"{self.cod_categoria} ({self.cod_idioma})"
    

    

class Especialidade(models.Model):
    cod_especialidade = models.CharField(max_length=50, primary_key=True)  # Código único
    descricao = models.CharField(max_length=255)  # Nome da especialidade
    ativo = models.BooleanField(default=True)  # Indica se está ativa ou inativa
    data_criacao = models.DateTimeField(auto_now_add=True)  # Data de criação automática
    data_atualizacao = models.DateTimeField(auto_now=True)  # Atualiza toda vez que for editado
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )  # Usuário responsável pela especialidade
    observacao = models.TextField(blank=True, null=True)  # Notas adicionais

    def __str__(self):
        return f"{self.descricao} ({'Ativo' if self.ativo else 'Inativo'})"



class MatrizPadraoAtividade(models.Model): 
    cod_matriz = models.CharField(max_length=50)  # Código único da matriz
    cod_categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)  
    cod_especialidade = models.ForeignKey('Especialidade', on_delete=models.CASCADE)  
    cod_atividade = models.CharField(max_length=50, blank=True, null=True)  
    cod_centro_trab = models.CharField(max_length=50)  
    ativo = models.BooleanField(default=True)  

    class Meta:
        unique_together = ('cod_matriz', 'cod_atividade')  # Evita registros duplicados

    def __str__(self):
        return f"{self.cod_matriz} - {self.cod_atividade} ({'Ativo' if self.ativo else 'Inativo'})"




class Criticidade(models.Model):
    cod_criticidade = models.CharField(max_length=50, primary_key=True)
    descricao = models.CharField(max_length=255)
    nivel = models.IntegerField()

    def __str__(self):
        return f"{self.descricao} (Nível {self.nivel})"


class ChaveModelo(models.Model):
    cod_chave = models.CharField(max_length=50, primary_key=True)
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.descricao



class CicloManutencao(models.Model):
    TIPO_INTERVALO_CHOICES = [
        ('D', 'Dias'),
        ('S', 'Semanas'),
        ('M', 'Meses'),
        ('A', 'Anos')
    ]

    cod_ciclo = models.CharField(max_length=50, primary_key=True)
    descricao = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="ciclos")
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE, related_name="ciclos")
    intervalo = models.IntegerField()
    tipo_intervalo = models.CharField(max_length=1, choices=TIPO_INTERVALO_CHOICES)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.descricao} ({self.get_tipo_intervalo_display()} - {self.intervalo})"
