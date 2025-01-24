from .models import ChatHistory , ChatSession
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout , authenticate
from .forms import CustomUserCreationForm, CustomLoginForm
from .services import processar_comunicacao_multi_ia
from django.shortcuts import get_object_or_404
from usuarios.provedores import processar_comunicacao_multi_ia, gerar_contexto_completo
from django.utils.safestring import mark_safe
from usuarios.provedores import formatar_texto_para_html
from django.contrib.auth import get_user_model
User = get_user_model() 
from django.urls import reverse
from .forms import CustomUserUpdateForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
PROVEDORES_VALIDOS = ['openai', 'gemini', 'llama']


def home(request):
    """Página inicial com informações sobre a QuickEAM."""
    return render(request, 'usuarios/home.html', {'pagina_atual': 'home'})


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
        
    return render(request, 'usuarios/register.html', {'form': form, 'pagina_atual': 'register'})


def user_login(request):
    errormessage = None
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username_or_cnpj = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username_or_cnpj, password=password)
            if user:
                login(request, user)
                return redirect('chat')
            else:
                messages.error(request, "Usuário ou CNPJ e senha inválidos.")
    else:
        form = CustomLoginForm()
    return render(request, 'usuarios/login.html', {'form': form, 'errormessage': errormessage, 'pagina_atual': 'login'})

@login_required
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

            # 🔄 Formata a resposta para HTML antes de salvar e exibir
            ai_response_formatado = formatar_texto_para_html(ai_response)

            # Salva a mensagem e a resposta no histórico
            ChatHistory.objects.create(
                session=session,
                user=request.user,
                question=user_message,
                answer=ai_response_formatado
            )

    # Recupera o histórico da sessão atual
    chat_history = ChatHistory.objects.filter(session=session).order_by('timestamp') if session else []
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    # Marcar como seguro para renderizar no template
    chat_history = [
        {
            'question': mensagem.question,
            'answer': mark_safe(mensagem.answer),  # Permite renderizar HTML seguro
        }
        for mensagem in chat_history
    ]

    return render(request, 'usuarios/chat.html', {
        'response': ai_response,
        'chat_history': chat_history,
        'sessions': sessions,
        'current_session': session,
        'pagina_atual': 'chat'
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


@login_required
def perfil(request):
    """Exibe e permite atualizar os dados do usuário logado com mensagens de feedback"""
    
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)  # Adicionamos request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso!")
            return redirect('perfil')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, 'usuarios/perfil.html', {'form': form, 'pagina_atual': 'perfil'})


@login_required
def deletar_conta(request):
    """Exclui a conta do usuário logado"""
    user = request.user
    user.delete()
    return redirect('home') # Redireciona para a página inicial após excluir


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            # Gera o ID do usuário e o token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Gera o link de redefinição
            reset_link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

            # Enviar e-mail com o link
            subject = "Redefinição de Senha - QuickEAM"
            message = f"Clique no link para redefinir sua senha: {reset_link}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            messages.success(request, "Um e-mail foi enviado com instruções para redefinir sua senha.")
            return redirect("password_reset_request")

        else:
            messages.error(request, "Nenhuma conta encontrada com este e-mail.")
    
    return render(request, "usuarios/password_reset_request.html")

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Senha redefinida com sucesso! Faça login com a nova senha.")
                return redirect("login")
            else:
                messages.error(request, "As senhas não coincidem.")

        return render(request, "usuarios/password_reset_confirm.html", {"valid_link": True})
    
    return render(request, "usuarios/password_reset_confirm.html", {"valid_link": False})





def logout_view(request):
    """Efetuar logout."""
    logout(request)
    return redirect('home')
