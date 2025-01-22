from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Formulário para registro de novos usuários."""
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj', 'password1', 'password2']

    def clean(self):
        """Validações customizadas para o formulário."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        cnpj = cleaned_data.get("cnpj")

        if not email and not cnpj:
            raise forms.ValidationError("Você deve fornecer um e-mail ou CNPJ")

        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    """Formulário para login de usuários."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome de usuário ou CNPJ'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )


class CustomUserUpdateForm(forms.ModelForm):
    """Formulário para atualização de dados do usuário."""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nome de Usuário'}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'E-mail'}),
    )
    cnpj = forms.CharField(
        max_length=18,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'CNPJ (Opcional)'}),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj']

    def clean_cnpj(self):
        """Valida e normaliza o campo CNPJ."""
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            # Remove formatações como ., / e -
            cnpj = cnpj.strip().replace(".", "").replace("-", "").replace("/", "")
            # Verifica se o CNPJ já está em uso, exceto para o próprio usuário
            if CustomUser.objects.filter(cnpj=cnpj).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este CNPJ já está em uso.")
        return cnpj

    def clean_username(self):
        """Valida se o nome de usuário é único, exceto para o próprio usuário."""
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username
