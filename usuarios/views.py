import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import activate
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserCreationForm, CustomLoginForm
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import ChatSession, ChatHistory
from .provedores import gerar_contexto_completo
from .services import processar_comunicacao_multi_ia
from django.contrib.auth import authenticate, login
from usuarios.provedores import processar_comunicacao_multi_ia
from usuarios.provedores import gerar_resposta


PROVEDORES_VALIDOS = ['openai', 'gemini', 'llama']

@csrf_exempt
def definir_idioma(request):
    """
    Define o idioma com base na localização enviada pelo cliente.
    """
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            latitude = dados.get('latitude')
            longitude = dados.get('longitude')

            # Use uma API de geocodificação para determinar o país3

            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en"
            response = requests.get(url)
            dados_localizacao = response.json()

            pais = dados_localizacao.get('countryCode', 'EN')

            # Mapeia o país para o idioma
            mapa_idiomas = {
                'BR': 'pt-br',
                'US': 'en',
                'ES': 'es',
            }

            idioma = mapa_idiomas.get(pais, 'en')
            activate(idioma)
            request.session['django_language'] = idioma

            return JsonResponse({'status': 'Idioma definido', 'idioma': idioma})
        except Exception as e:
            return JsonResponse({'status': 'Erro', 'mensagem': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'Método não permitido'}, status=405)


def home(request):
    """Página inicial com informações sobre a QuickEAM."""
    return render(request, 'usuarios/home.html')


def register(request):
    """Cadastro de novos usuários."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso. Faça login.")
            return redirect('login')
        else:
            messages.error(request, "Erro ao realizar o cadastro. Verifique os dados.")

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
            messages.error(request, "Falha verifique Usuário ou Senha.")
    else:
        form = CustomLoginForm()
    return render(request, 'usuarios/login.html', {'form': form})


def chat(request, session_id=None):
    ai_response = None
    session = None

    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    elif request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            session = ChatSession.objects.create(user=request.user)

    if session and request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            if not session.title or session.title == "Nova Conversa":
                session.title = user_message[:40]
                session.save()

            historico_completo = ChatHistory.objects.filter(session=session).order_by('timestamp')
            contexto = gerar_contexto_completo(historico_completo)

            respostas = {}
            for provedor in PROVEDORES_VALIDOS:
                resposta = gerar_resposta(provedor, user_message, contexto)
                respostas[provedor] = resposta

            melhor_resposta = max(respostas.values(), key=lambda x: len(x))

            ChatHistory.objects.create(
                session=session,
                user=request.user,
                question=user_message,
                answer=melhor_resposta
            )

            ai_response = melhor_resposta

    chat_history = ChatHistory.objects.filter(session=session).order_by('timestamp') if session else []
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    if not session and not session_id:
        session = None

    return render(request, 'usuarios/chat.html', {
        'response': ai_response,
        'chat_history': chat_history,
        'sessions': sessions,
        'current_session': session,
    })




@login_required
def excluir_chat(request, session_id):
    try:
        chat_session = ChatSession.objects.get(id=session_id, user=request.user)
        chat_session.delete()
    except ChatSession.DoesNotExist:
        messages.error(request, "Conversa não encontrada ou não pertence a você.")
    return redirect('chat')  # Não cria nova sessão automaticamente


def logout_view(request):
    """
    Efetua logout do usuário e redireciona para a página inicial.
    """
    logout(request)
    return redirect('home')


@login_required
def editar_titulo(request, session_id):
    if request.method == 'POST':
        new_title = request.POST.get('new_title', '').strip()
        if new_title:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            session.title = new_title[:30]  # Limita o título a 30 caracteres
            session.save()
    return redirect('chat_session', session_id=session_id)
