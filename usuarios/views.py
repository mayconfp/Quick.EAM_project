from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatSession, ChatMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, CustomLoginForm
import requests
from django.http import JsonResponse
from django.utils import translation

PROVEDORES_VALIDOS = ['openai', 'gemini', 'llama']

@login_required
def new_chat(request):
    """Inicia uma nova sessão de chat."""
    session = ChatSession.objects.create(user=request.user)
    return redirect('chat', session_id=session.id)


def user_login(request):
    """Login de usuários."""
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            session, created = ChatSession.objects.get_or_create(user=user)
            return redirect('chat', session_id=session.id)
    else:
        form = CustomLoginForm()

    return render(request, 'usuarios/login.html', {'form': form})

def set_language_by_location(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        try:
            response = requests.get(
                f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en")
            country = response.json().get('countryName')

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


from random import choice

@login_required
def chat(request, session_id=None):
    if session_id is None:
        session = ChatSession.objects.create(user=request.user)
        return redirect('chat', session_id=session.id)

    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = ChatMessage.objects.filter(session=session)

    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            # Lógica simples para respostas do bot
            respostas_bot = [
                "Oi! Como posso ajudar você hoje?",
                "Tudo bem com você?",
                "Que bom te ver! O que gostaria de saber?",
                "Olá! Me conte mais sobre o que está pensando.",
            ]
            bot_response = choice(respostas_bot)

            ChatMessage.objects.create(
                session=session,
                user_message=user_message,
                bot_response=bot_response
            )
        return redirect('chat', session_id=session.id)

    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'usuarios/chat.html', {
        'chat_history': messages,
        'sessions': sessions,
        'current_session': session,
    })


@login_required
def new_chat(request):
    """Inicia uma nova sessão de chat."""
    session = ChatSession.objects.create(user=request.user)
    return redirect('chat', session_id=session.id)

def logout_view(request):
    """Efetuar logout."""
    logout(request)
    return redirect('home')
