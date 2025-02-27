from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .validators import validar_cnpj_existente
from .models import Categoria, CategoriaLang, Especialidade, MatrizPadraoAtividade, CicloPadrao, Criticidade, ChaveModelo



class CustomUserCreationForm(UserCreationForm):
    email=forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj', 'password1', 'password2', 'profile_picture']

    def clean_cnpj(self):
        """Valida e normaliza o campo CNPJ."""
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            # Normaliza o CNPJ
            cnpj = cnpj.strip().replace(".", "").replace("-", "").replace("/", "")
            # Valida com API e verifica unicidade
            validar_cnpj_existente(cnpj)
            if CustomUser.objects.filter(cnpj=cnpj).exists():
                raise ValidationError("Este CNPJ já está cadastrado.")
        return cnpj


    def clean(self):
        """Validações gerais."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        cnpj = cleaned_data.get("cnpj")

        if not email and not cnpj:
            raise forms.ValidationError("Você deve fornecer um e-mail ou CNPJ.")
        return cleaned_data

    def save(self, commit=True):
        """Salva os dados normalizados."""
        user = super().save(commit=False)
        if self.cleaned_data.get('cnpj'):
            user.cnpj = self.cleaned_data.get('cnpj').strip()
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('pt', 'Português'),
        ('es', 'Español'),
    ]
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Usuário ou CNPJ'}),
        label="Usuário ou CNPJ"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}),
        label="Senha"
    )
    idioma = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=True, label="Idioma")

    def clean_username(self):
        username_or_cnpj = self.cleaned_data.get('username')
        if username_or_cnpj:
            username_or_cnpj = username_or_cnpj.strip()  # Remove espaços extras
        return username_or_cnpj


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
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'custom-file-input'}),
        label="Foto do Perfil",
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'profile_picture']  # 🔥 Removemos 'cnpj'

    def clean_username(self):
        """Valida a unicidade do nome de usuário apenas se ele foi alterado."""
        username = self.cleaned_data.get('username')
        if username and username != self.instance.username:
            if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        """Valida a unicidade do e-mail apenas se ele foi alterado."""
        email = self.cleaned_data.get('email')
        if email and email != self.instance.email:
            if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este e-mail já está em uso.")
        return email

#att

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['cod_categoria', 'cod_categoria_pai', 'descricao']  # Adicionado 'descricao'
        labels = {
            'cod_categoria': 'Código da Categoria',
            'cod_categoria_pai': 'Categoria Pai',
            'descricao': 'Descrição',
        }


class CategoriaLangForm(forms.ModelForm):
    class Meta:
        model = CategoriaLang
        fields = ['cod_categoria', 'cod_idioma', 'descricao']
        labels = {
            'cod_categoria': 'Código da Categoria',
            'cod_idioma': 'Idioma',
            'descricao': 'Descrição Traduzida'
        }


class EspecialidadeForm(forms.ModelForm):
    class Meta:
        model = Especialidade
        fields = ['cod_especialidade', 'descricao']
        labels = {
            'cod_especialidade': 'Código da Especialidade',
            'descricao': 'Descrição'
        }


class MatrizPadraoAtividadeForm(forms.ModelForm):
    class Meta:
        model = MatrizPadraoAtividade
        fields = ['cod_categoria', 'cod_especialidade']
        labels = {
            'cod_categoria': 'Categoria',
            'cod_especialidade': 'Especialidade'
        }


class CicloPadraoForm(forms.ModelForm):
    class Meta:
        model = CicloPadrao
        fields = ['cod_ciclo', 'descricao', 'intervalo_dias']
        labels = {
            'cod_ciclo': 'Código do Ciclo',
            'descricao': 'Descrição',
            'intervalo_dias': 'Intervalo em Dias'
        }


class CriticidadeForm(forms.ModelForm):
    class Meta:
        model = Criticidade
        fields = ['cod_criticidade', 'descricao', 'nivel']
        labels = {
            'cod_criticidade': 'Código da Criticidade',
            'descricao': 'Descrição',
            'nivel': 'Nível de Criticidade'
        }


class ChaveModeloForm(forms.ModelForm):
    class Meta:
        model = ChaveModelo
        fields = ['cod_chave', 'descricao']
        labels = {
            'cod_chave': 'Código da Chave',
            'descricao': 'Descrição'
        }
