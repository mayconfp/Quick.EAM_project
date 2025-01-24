from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj', 'password1', 'password2', 'profile_picture']

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            cnpj = cnpj.strip().replace(".", "").replace("-", "").replace("/", "")  # Normaliza o CNPJ
            validar_cnpj_existente(cnpj)  # Valida com API
        return cnpj

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('cnpj'):
            user.cnpj = self.cleaned_data.get('cnpj').strip()
        if commit:
            user.save()
        return user


    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            cnpj = cnpj.strip().replace(".", "").replace("-", "").replace("/", "")
            if CustomUser.objects.filter(cnpj=cnpj).exists():
                raise ValidationError("Este CNPJ já está cadastrado.")
        return cnpj


    def clean(self):
        """Validações customizadas para o formulário."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        cnpj = cleaned_data.get("cnpj")

        if not email and not cnpj:
            raise forms.ValidationError("Você deve fornecer um e-mail ou CNPJ")

        return cleaned_data

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Usuário ou CNPJ'}),
        label="Usuário ou CNPJ"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}),
        label="Senha"
    )

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
    cnpj = forms.CharField(
        max_length=18,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'CNPJ (Opcional)'}),
    )

    profile_picture = forms.ImageField(
        required=False,  # Permite que o usuário não envie uma imagem
        widget=forms.ClearableFileInput(attrs={'class': 'custom-file-input'}),
        label="Foto de Perfil"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj', 'profile_picture']  # Certifique-se de incluir 'profile_picture' aqui

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

    def save(self, commit=True):
        """Sobrescreve o método save para lidar com o arquivo de imagem."""
        user = super().save(commit=False)  # Salva os dados principais do formulário, mas não no banco ainda
        if 'profile_picture' in self.files:  # Verifica se há uma imagem no POST
            user.profile_picture = self.files['profile_picture']  # Atribui o arquivo enviado ao campo do modelo
        if commit:
            user.save()  # Salva no banco de dados
        return user


#

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
