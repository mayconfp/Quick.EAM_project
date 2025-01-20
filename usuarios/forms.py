from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from usuarios.validators import validate_custom_username


class CustomUserCreationForm(UserCreationForm):
    """Formulário de registro de novos usuários."""
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[validate_custom_username],  # Aplica o validador personalizado
        widget=forms.TextInput(attrs={'placeholder': 'Usuário'}),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Verifica se o username já está em uso
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        try:
            validate_password(password)  # Valida a segurança da senha
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password


class CustomLoginForm(AuthenticationForm):
    """Formulário para login de usuários."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Usuário ou CNPJ'}),
        label="Usuário ou CNPJ"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}),
        label="Senha"
    )

class CustomUserUpdateForm(forms.ModelForm):
    """Formulário para atualização de dados do usuário."""
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[validate_custom_username],
        widget=forms.TextInput(attrs={'placeholder': 'Usuário'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'E-mail'}),
    )
    cnpj = forms.CharField(
        max_length=14,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'CNPJ (Opcional)'}),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Permite que o usuário mantenha seu próprio username sem erro
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            # Normaliza o CNPJ removendo formatações
            cnpj = cnpj.strip().replace(".", "").replace("-", "").replace("/", "")
            if CustomUser.objects.filter(cnpj=cnpj).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este CNPJ já está em uso.")
        return cnpj

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError
from usuarios.validators import validate_custom_username  # Validador personalizado, se necessário

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Usuário'}),
    )
    cnpj = forms.CharField(
        max_length=18,
        required=False,  # CNPJ é opcional
        widget=forms.TextInput(attrs={'placeholder': 'CNPJ (Opcional)'}),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj', 'password1', 'password2']

    def clean_cnpj(self):
        """Valida e normaliza o CNPJ, se fornecido."""
        cnpj = self.cleaned_data.get('cnpj')

        # Ignora validação se o CNPJ não foi preenchido
        if not cnpj:
            return cnpj

        # Normaliza o CNPJ (remove caracteres como . - /)
        cnpj = cnpj.strip().replace(".", "").replace("-", "").replace("/", "")

        # Verifica se já existe no banco de dados
        if CustomUser.objects.filter(cnpj=cnpj).exists():
            raise ValidationError("Este CNPJ já está cadastrado. Por favor, utilize outro.")

        return cnpj
