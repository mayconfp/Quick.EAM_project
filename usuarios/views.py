from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser
from .openai_cliente import gerar_resposta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .openai_cliente import gerar_resposta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usuarios.openai_cliente import gerar_resposta

@login_required
def chat_view(request):
    ai_response = None

    if request.method == "POST":
        user_message = request.POST.get("message")
        print(f"Mensagem do usuário: {user_message}")

        if user_message:
            # Chama a função que gera a resposta e salva no histórico
            ai_response = gerar_resposta(user_message, user=request.user)

    return render(request, 'usuarios/chat.html', {'response': ai_response})


def home(request):
    """Página inicial com informações sobre a QuickEAM."""
    return render(request, 'usuarios/home.html')

def register(request):
    """Cadastro de novos usuários."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'usuarios/register.html', {'form': form})

def user_login(request):
    """Login de usuários."""
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat')
    else:
        form = CustomLoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

@login_required
def chat(request):
    """Página do chat com a IA."""
    ai_response = None
    if request.method == 'POST':
        user_message = request.POST.get('message')  # Obtém mensagem do usuário
        ai_response = gerar_resposta(user_message)  # Gera resposta da IA
    return render(request, 'usuarios/chat.html', {'response': ai_response})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def listar_usuarios(request):
    """Listagem de usuários (restrita a administradores)."""
    users = CustomUser.objects.all()
    return render(request, 'usuarios/listar.html', {'users': users})

def logout_view(request):
    """Efetuar logout."""
    logout(request)
    return redirect('home')
