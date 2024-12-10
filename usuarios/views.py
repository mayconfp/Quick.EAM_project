from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser, ChatHistory
from .openai_cliente import gerar_resposta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .openai_cliente import gerar_resposta

import logging
logger = logging.getLogger(__name__)

@login_required
def chat(request):
    ai_response = None
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if not user_message:
            logger.error("Mensagem do usuário é inválida.")
            return render(request, 'usuarios/chat.html', {'response': "Mensagem inválida."})

        # Verificar se a pergunta já existe no banco
        historico = ChatHistory.objects.filter(user=request.user, question__iexact=user_message).first()
        if historico:
            ai_response = historico.answer
            logger.info(f"Resposta recuperada do banco: {ai_response}")
        else:
            ai_response = gerar_resposta(user_message)
            if ai_response:
                ChatHistory.objects.create(
                    user=request.user,
                    question=user_message,
                    answer=ai_response
                )
                logger.info(f"Nova conversa salva: {user_message} - {ai_response}")

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
