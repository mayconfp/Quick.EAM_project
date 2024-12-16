from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from usuarios.models import ChatHistory, CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Formulário para cadastro de novos usuários."""
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class CustomLoginForm(AuthenticationForm):
    """Formulário para login de usuários."""
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Usuário'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
