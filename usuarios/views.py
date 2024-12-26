from .models import ChatHistory
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, CustomLoginForm
from .services import processar_comunicacao_multi_ia, recuperar_ultima_resposta


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


from .services import processar_comunicacao_multi_ia, recuperar_ultima_resposta

@login_required
def chat(request):
    ai_response = None
    provedor_selecionado = 'openai'  # Valor padrão

    if request.method == 'POST':
        # Obtém a mensagem e o provedor selecionado
        user_message = request.POST.get('message', '').strip()
        provedor_selecionado = request.POST.get('provedor', 'openai')

        print(f"[DEBUG] Mensagem do usuário: {user_message}")
        print(f"[DEBUG] Provedor selecionado: {provedor_selecionado}")

        # Detecta comandos especiais
        if "resuma" in user_message.lower() or "traduza" in user_message.lower():
            # Recupera a última resposta salva no banco
            ultima_resposta = recuperar_ultima_resposta(request.user)

            if ultima_resposta:
                # Concatena a mensagem e a resposta anterior
                comando_especial = f"{user_message}. O texto a ser processado é: {ultima_resposta}"
                print(f"[DEBUG] Executando comando especial: {comando_especial}")
                ai_response = processar_comunicacao_multi_ia(comando_especial)
            else:
                ai_response = "Nenhuma mensagem anterior encontrada para processar."
        else:
            # Processa a mensagem normalmente
            ai_response = processar_comunicacao_multi_ia(user_message)

        # Salva a mensagem e a resposta no banco
        ChatHistory.objects.create(
            user=request.user,
            question=user_message,
            answer=ai_response,
            ia_used=provedor_selecionado
        )


    # Recupera o histórico completo do banco de dados
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
