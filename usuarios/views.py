from .gemini_cliente import gemini_gerar_resposta
from .llama_cliente import gerar_resposta_llama
from .models import ChatHistory, ChatSession
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm
from .openai_cliente import gerar_resposta_openai
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import activate

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

            # Use uma API de geocodificação para determinar o país
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
            form.save()
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
            messages.error(request, "Login falhou. Verifique suas credenciais.")
    else:
        form = CustomLoginForm()
    return render(request, 'usuarios/login.html', {'form': form})


from django.shortcuts import get_object_or_404

@login_required
def chat(request, session_id=None):
    ai_response = None
    provedor_selecionado = 'openai'

    # Recupera ou cria uma nova sessão
    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    else:
        session = ChatSession.objects.create(user=request.user)

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        provedor_selecionado = request.POST.get('provedor', 'openai')

        if provedor_selecionado not in PROVEDORES_VALIDOS:
            provedor_selecionado = 'openai'

        # Atualiza o título da sessão com a primeira mensagem
        if not ChatHistory.objects.filter(session=session).exists():
            session.title = user_message[:30]  # Usa os primeiros 30 caracteres da mensagem
            session.save()

        # Construa o contexto com base no histórico da sessão
        chat_history = ChatHistory.objects.filter(session=session).order_by('timestamp')
        contexto = [{"role": "user", "content": chat.question} if chat.user else {"role": "assistant", "content": chat.answer} for chat in chat_history]

        # Adiciona a mensagem atual do usuário ao contexto
        contexto.append({"role": "user", "content": user_message})

        # Processa a mensagem diretamente com o provedor selecionado
        if provedor_selecionado == 'openai':
            ai_response = gerar_resposta_openai(user_message, contexto)
        elif provedor_selecionado == 'llama':
            ai_response = gerar_resposta_llama(user_message, contexto)
        elif provedor_selecionado == 'gemini':
            ai_response = gemini_gerar_resposta(user_message)

        # Salva no histórico
        ChatHistory.objects.create(
            session=session,
            user=request.user,
            question=user_message,
            answer=ai_response,
            ia_used=provedor_selecionado
        )

    # Recupera o histórico atualizado
    chat_history = ChatHistory.objects.filter(session=session).order_by('timestamp')
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'usuarios/chat.html', {
        'response': ai_response,
        'chat_history': chat_history,
        'sessions': sessions,
        'current_session': session,
        'provedor_selecionado': provedor_selecionado
    })



def logout_view(request):
    """Efetuar logout."""
    logout(request)
    messages.info(request, "Você saiu com sucesso.")
    return redirect('home')
