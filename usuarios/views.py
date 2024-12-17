from .services import processar_pergunta_com_respostas
from .models import ChatHistory
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, CustomLoginForm

PROVEDORES_VALIDOS = ['openai', 'gemini', 'llama']

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
    """Função principal do chat."""
    ai_response = None

    if request.method == 'POST':
        # Captura a mensagem do usuário e a IA escolhida
        user_message = request.POST.get('message')
        ia_escolhida = request.POST.get('provedor', 'openai').lower()

        # Valida o provedor escolhido
        if ia_escolhida not in PROVEDORES_VALIDOS:
            ia_escolhida = 'openai'  # Define padrão se o valor for inválido

        if user_message:
            # Gera a resposta com base no histórico e nas respostas auxiliares
            ai_response = processar_pergunta_com_respostas(user_message, ia_escolhida)

            # Salva no histórico
            ChatHistory.objects.create(
                user=request.user,
                question=user_message,
                answer=ai_response,
                ia_used=ia_escolhida
            )

    # Recupera o histórico de chat
    chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')

    return render(request, 'usuarios/chat.html', {
        'response': ai_response,
        'chat_history': chat_history,
    })

def logout_view(request):
    """Efetuar logout."""
    logout(request)
    return redirect('home')
