from django.core.exceptions import ValidationError
import re

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