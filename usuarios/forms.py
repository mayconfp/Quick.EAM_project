from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cnpj', 'password1', 'password2' ]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        cnpj = cleaned_data.get("cnpj")

        if not email and not cnpj:
            raise forms.ValidationError ("Você deve fornecer um e-mail ou CNPJ")

        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Digite seu nome de usuário ou e-mail'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Digite sua senha'
    }))

