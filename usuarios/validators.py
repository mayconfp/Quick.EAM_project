from django.core.exceptions import ValidationError
import re
import requests
from django.core.exceptions import ValidationError
from django.conf import settings


def validar_cnpj_existente(cnpj):
    """
    Consulta o CNPJ na API BrasilAPI e verifica se é válido e ativo.
    """
    url = f"{settings.BRASIL_API_URL}{cnpj}"
    response = requests.get(url)

    if response.status_code == 404:
        raise ValidationError("CNPJ não encontrado ou empresa inexistente.")
    elif response.status_code != 200:
        raise ValidationError("Erro ao validar o CNPJ. Tente novamente mais tarde.")

    data = response.json()
    if data.get("situacao_cadastral") != 2:  # 2 significa 'Ativa'
        raise ValidationError("CNPJ encontrado, mas a empresa não está ativa.")


class SenhaPersonalizada:
    def validate (self , password , user = None):
        if len(password) < 8:
            raise ValidationError("Essa senha deve conter pelo menos uma Letra Maiúscula.")
        if not any(char.isupper() for char in password):
            raise ValidationError("Sua senha deve conter pelo menos 8 caracteres.")
        if not any(char in "!@#$%^&*" for char in password):
            raise ValidationError("A Senha deve conter pelo menos um caractere especial.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("A Senha deve conter pelo menos um número.")

    def get_help_text(self):
        return ("Sua senha deve conter pelo menos uma letra maiúscula e um caractere especial."
                "Sua senha deve conter pelo menos 8 caracteres e um número"
        )

def validate_custom_username(username):
    if len(username) < 5:
        raise ValidationError("O nome de usuário deve ter pelo menos 5 caracteres.")
    if not username.isalnum():
        raise ValidationError("O nome de usuário deve conter apenas letras e números.")
    if username.lower() == "admin":
        raise ValidationError("Este nome de usuário não é permitido.")
    

    
def validate_cnpj(cnpj):
    """
    Valida um CNPJ brasileiro.
    """
    cnpj = re.sub(r'\D', '', cnpj)  # Remove caracteres não numéricos

    if len(cnpj) != 14:
        raise ValidationError("O CNPJ deve conter exatamente 14 números.")

    if cnpj in ("00000000000000", "11111111111111", "22222222222222",
                "33333333333333", "44444444444444", "55555555555555",
                "66666666666666", "77777777777777", "88888888888888",
                "99999999999999"):
        raise ValidationError("CNPJ inválido.")

    def calculate_digit(cnpj, weights):
        soma = sum(int(a) * b for a, b in zip(cnpj, weights))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    weights_first_digit = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_second_digit = [6] + weights_first_digit

    # Verifica os dois dígitos verificadores
    if calculate_digit(cnpj[:12], weights_first_digit) != cnpj[12] or \
       calculate_digit(cnpj[:13], weights_second_digit) != cnpj[13]:
        raise ValidationError("CNPJ inválido.")
