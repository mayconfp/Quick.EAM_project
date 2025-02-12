from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

UserModel = get_user_model()

class UsernameOrCNPJBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Autentica o usuário com base no username ou CNPJ."""
        if not username or not password:
            logger.warning("Username ou senha não fornecidos.")
            return None


        try:
            # Tenta buscar o usuário pelo username
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            try:
                # Tenta buscar o usuário pelo CNPJ
                user = UserModel.objects.get(cnpj=username)
            except UserModel.DoesNotExist:
                logger.warning(f"Usuário com username ou CNPJ '{username}' não encontrado.")
                return None

        # Verifica a senha
        if user.check_password(password):
            logger.info(f"Usuário autenticado com sucesso: {username}")
            return user
        else:
            logger.warning(f"Senha inválida para o usuário: {username}")
            return None

    def get_user(self, user_id):
        """Busca um usuário pelo ID."""
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            logger.warning(f"Usuário com ID '{user_id}' não encontrado.")
            return None