from .models import ChatHistory , ChatSession
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, CustomLoginForm
from .services import processar_comunicacao_multi_ia
from django.shortcuts import get_object_or_404
from usuarios.provedores import processar_comunicacao_multi_ia, gerar_contexto_completo


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
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'usuarios/register.html', {'form': form})


def user_login(request):
    errormessage = None
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat')
        else:
            errormessage ="Usuário ou senha incorretos"
    else:
        form = CustomLoginForm()
    return render(request, 'usuarios/login.html', {'form': form, 'errormessage': errormessage })


def chat(request):
    ai_response = None
    session_id = request.GET.get('session')
    session = None

    # Carrega ou cria uma nova sessão
    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    else:
        session = ChatSession.objects.filter(user=request.user).order_by('-created_at').first()

    if not session:
        return redirect('nova_conversa')

    # Processa a mensagem do usuário
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            if not session.title or session.title == "Nova Conversa":
                session.title = user_message[:30]
                session.save()

            # 🔄 Gera o contexto completo com base no histórico
            historico_completo = ChatHistory.objects.filter(session=session).order_by('timestamp')

            contexto_para_openai = gerar_contexto_completo(historico_completo)

            # 🧠 Chama a função que processa a mensagem com múltiplas IAs
            ai_response = processar_comunicacao_multi_ia(user_message, contexto_para_openai)

            # Salva a mensagem e a resposta no histórico
            ChatHistory.objects.create(
                session=session,
                user=request.user,
                question=user_message,
                answer=ai_response
            )

    # Recupera o histórico da sessão atual
    chat_history = ChatHistory.objects.filter(session=session).order_by('timestamp') if session else []
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'usuarios/chat.html', {
        'response': ai_response,
        'chat_history': chat_history,
        'sessions': sessions,
        'current_session': session,
})

@login_required
def nova_conversa(request):
    if request.method == 'POST':
        # Cria uma nova sessão de conversa
        new_session = ChatSession.objects.create(user=request.user, title="Nova Conversa")
        return redirect(f"/chat/?session={new_session.id}")

    # Garante que a criação da sessão funcione corretamente
    if not ChatSession.objects.filter(user=request.user).exists():
        new_session = ChatSession.objects.create(user=request.user, title="Nova Conversa")
        return redirect(f"/chat/?session={new_session.id}")

    # Se houver uma sessão existente, redireciona para a última
    last_session = ChatSession.objects.filter(user=request.user).order_by('-created_at').first()
    if last_session:
        return redirect(f"/chat/?session={last_session.id}")

    return redirect('chat')


@login_required
def deletar_conversa(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()
    return redirect('chat')

def logout_view(request):
    """Efetuar logout."""
    logout(request)
    return redirect('home')
