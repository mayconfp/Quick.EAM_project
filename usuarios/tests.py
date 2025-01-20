from django.test import TestCase
from usuarios.forms import CustomUserCreationForm
from usuarios.models import CustomUser

class CustomUserCreationFormTest(TestCase):
    def test_register_without_cnpj(self):
        """Testa registro de usuário sem CNPJ (CNPJ opcional)."""
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'SecureP@ssw0rd',
            'password2': 'SecureP@ssw0rd',
        })
        self.assertTrue(form.is_valid(), msg=f"Erros no formulário: {form.errors}")

    def test_register_with_cnpj(self):
        """Testa registro de usuário com CNPJ válido."""
        form = CustomUserCreationForm(data={
            'username': 'user_with_cnpj',
            'email': 'user@example.com',
            'cnpj': '12345678000199',
            'password1': 'SecureP@ssw0rd',
            'password2': 'SecureP@ssw0rd',
        })
        self.assertTrue(form.is_valid(), msg=f"Erros no formulário: {form.errors}")

    def test_register_with_duplicate_cnpj(self):
        """Testa registro de usuário com CNPJ duplicado."""
        CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            cnpj='12345678000199',
            password='SecureP@ssw0rd',
        )
        form = CustomUserCreationForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'cnpj': '12345678000199',  # CNPJ duplicado
            'password1': 'SecureP@ssw0rd',
            'password2': 'SecureP@ssw0rd',
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Este CNPJ já está cadastrado. Por favor, utilize outro.", form.errors['cnpj'])

    def test_register_with_invalid_password(self):
        """Testa registro com senha inválida."""
        form = CustomUserCreationForm(data={
            'username': 'user_invalid_password',
            'email': 'invalidpassword@example.com',
            'password1': '1234',  # Senha muito fraca
            'password2': '1234',
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Essa senha deve conter pelo menos uma Letra Maiúscula.", str(form.errors['password1']))

    def test_register_with_mismatched_passwords(self):
        """Testa registro com senhas que não correspondem."""
        form = CustomUserCreationForm(data={
            'username': 'user_mismatch_password',
            'email': 'mismatch@example.com',
            'password1': 'SecureP@ssw0rd',
            'password2': 'DifferentP@ssw0rd',  # Senhas diferentes
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Os dois campos de senha não correspondem.", str(form.errors['password2']))
