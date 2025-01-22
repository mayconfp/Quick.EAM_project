from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomLoginForm, CustomUserUpdateForm
from .models import CustomUser, ChatSession, ChatHistory
from .provedores import gerar_contexto_completo, gerar_resposta, processar_comunicacao_multi_ia
from .provedores import formatar_texto_para_html
from django.utils.translation import activate
from django.utils.safestring import mark_safe
import requests


PROVEDORES_VALIDOS = ['openai', 'gemini', 'llama']



def definir_idioma(request):
    """Define o idioma com base na localização enviada pelo cliente."""
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
    return render(request, 'usuarios/home.html', {'pagina_atual': 'home'})




def register(request):
    """Cadastro de novos usuários."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado com sucesso! Agora você pode fazer login.')
            return redirect('login')
        else:
            messages.error(request, "Erro ao realizar o cadastro. Verifique os dados.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'usuarios/register.html', {'form': form, 'pagina_atual': 'register'})




def user_login(request):
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

    return render(request, 'usuarios/login.html', {'form': form})



def logout_view(request):
    """Efetua logout do usuário e redireciona para a página inicial."""
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('home')




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
def excluir_chat(request, session_id):
    """Exclui uma conversa específica."""
    try:
        chat_session = ChatSession.objects.get(id=session_id, user=request.user)
        chat_session.delete()
    except ChatSession.DoesNotExist:
        messages.error(request, "Conversa não encontrada ou não pertence a você.")
    return redirect('chat')





@login_required
def perfil(request):
    """Exibe e permite atualizar os dados do usuário logado."""
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso!")
            return redirect('chat')
        else:
            messages.error(request, "Erro ao atualizar o perfil. Verifique os dados.")
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, 'usuarios/perfil.html', {'form': form, 'pagina_atual': 'perfil'})




@login_required
def deletar_conta(request):
    """Exclui a conta do usuário logado."""
    user = request.user
    user.delete()
    messages.success(request, "Sua conta foi excluída com sucesso.")
    return redirect('home')
