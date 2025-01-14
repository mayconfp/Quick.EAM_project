from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from usuarios.validators  import validate_custom_username



class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[validate_custom_username],  # Aplica o validador personalizado
        widget=forms.TextInput(attrs={'placeholder': 'Usuário ou CNPJ'}),
    )
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Garante que o nome de usuário é único
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        try:
            validate_password(password, user=None)  # Aplica todas as validações registradas
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password

class CustomLoginForm(AuthenticationForm):
    """Formulário para login de usuários."""
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Usuário'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
