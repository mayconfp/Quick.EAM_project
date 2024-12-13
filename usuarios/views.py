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
    ai_response = None
    provedor_selecionado = 'openai'  # Valor padrão caso o usuário não escolha nenhum

    if request.method == 'POST':
        # Obtém a mensagem e o provedor selecionado
        user_message = request.POST.get('message')
        provedor_selecionado = request.POST.get('copilot', 'openai')

        # Chama o serviço de processamento
        ai_response = process_chat_message(request.user, user_message, provedor_selecionado)

    # Recupera o histórico e renderiza o template
    chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')

    return render(request, 'usuarios/chat.html', {
        'response': ai_response,
        'chat_history': chat_history,
        'provedor_selecionado': provedor_selecionado
    })



def logout_view(request):
    """Efetuar logout."""
    logout(request)
    return redirect('home')