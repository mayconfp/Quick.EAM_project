from .services import processar_pergunta_com_respostas
from .models import ChatHistory
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, CustomLoginForm
import requests
from django.http import JsonResponse
from django.utils import translation


PROVEDORES_VALIDOS = ['openai', 'gemini', 'llama']

def set_language_by_location(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # Usar API de geolocalização para obter o país
        try:
            response = requests.get(f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en")
            country = response.json().get('countryName')

            # Define o idioma com base no país
            if country in ['Brazil', 'Portugal']:
                translation.activate('pt-br')
                request.session[translation.LANGUAGE_SESSION_KEY] = 'pt-br'
            else:
                translation.activate('en')
                request.session[translation.LANGUAGE_SESSION_KEY] = 'en'

        except Exception as e:
            print(f"Erro ao detectar localização: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "method not allowed"}, status=405)


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
@login_required
@login_required
def chat(request):
    """Função principal do chat."""
    ai_response = None

    if request.method == 'POST':
        # Captura a mensagem do usuário
        user_message = request.POST.get('message')

        if user_message:
            # Gera a resposta usando OpenAI e outras IAs auxiliares
            ai_response = processar_pergunta_com_respostas(user_message, request.user)

            # Salva no histórico
            ChatHistory.objects.create(
                user=request.user,
                question=user_message,
                answer=ai_response,
                ia_used='openai'
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
