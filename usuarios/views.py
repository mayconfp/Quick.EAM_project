from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser, ChatHistory
from .openai_cliente import gerar_resposta
from .gemini_cliente import gemini_gerar_respota  # Importa a função para usar o Gemini


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

#metodos do chat para banco e etc
@login_required
def chat(request):
    """Página do chat com a escolha entre GPT e Gemini."""
    ai_response = None  # Inicializa a variável para a resposta da IA

    if request.method == 'POST':
        user_message = request.POST.get('message')  # Mensagem do usuário
        ia_choice = request.POST.get('ia_choice')  # Escolha da IA (GPT ou Gemini)

        if user_message and ia_choice:
            if ia_choice == 'GPT':  # Caso escolha o OpenAI
                ai_response = gerar_resposta(user_message)
            elif ia_choice == 'Gemini':  # Caso escolha o Gemini
                ai_response = gemini_gerar_respota(user_message)

            # Salva a interação no banco de dados
            ChatHistory.objects.create(
                user=request.user,
                question=user_message,
                answer=ai_response,
                ia_used=ia_choice  # Registra qual IA foi usada
            )

    # Recupera o histórico de mensagens para o usuário atual, ordenado por data
    chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')

    # Renderiza a página do chat com a resposta e o histórico
    return render(request, 'usuarios/chat.html', {
        'response': ai_response,
        'chat_history': chat_history
    })


def logout_view(request):
    """Efetuar logout."""
    logout(request)
    return redirect('home')