from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser, ChatHistory
from .services import process_chat_message


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
    provedor_selecionado = 'openai'  # Valor padrão

    if request.method == 'POST':
        # Captura a mensagem do usuário e o provedor selecionado
        user_message = request.POST.get('message')
        provedor_selecionado = request.POST.get('provedor', 'openai')

        # Garante que process_chat_message é chamado apenas uma vez
        if user_message:
            ai_response = process_chat_message(request.user, user_message, provedor_selecionado)

    # Recupera o histórico completo do banco de dados
    chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')

    # Renderiza o template com o histórico e o provedor selecionado
    return render(request, 'usuarios/chat.html', {
        'chat_history': chat_history,
        'provedor_selecionado': provedor_selecionado
    })



def logout_view(request):
    """Efetuar logout."""
    logout(request)
    return redirect('home')