from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import activate
from .models import Categoria, CategoriaLang
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .validators import SenhaPersonalizada
from django.core.exceptions import ValidationError
from .forms import CustomUserCreationForm, CustomLoginForm, CustomUserUpdateForm , EspecialidadeForm,CicloManutencao , MatrizPadraoAtividadeForm, CicloPadraoForm
from .models import ChatSession, ChatHistory ,MatrizPadraoAtividade, Categoria, Especialidade,CicloManutencao, CategoriaLang, PasswordResetCode
from .provedores import formatar_texto_para_html, processar_comunicacao_multi_ia
from .services import gerar_resposta, recuperar_ultima_resposta
from django.db import DatabaseError
import pymupdf as fitz
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .openai_cliente import buscar_no_json, carregar_conhecimento, processar_arquivo
import requests
import logging
import json
import os
import markdown 
from django.utils.safestring import mark_safe

PROVEDORES_VALIDOS = ['openai', 'gemini', 'llama']


logger = logging.getLogger(__name__)  # Cria um logger para este módulo


@login_required
def perfil(request):
    """Exibe e permite atualizar os dados do usuário logado."""
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso!")
            return redirect('perfil')
        else:
            messages.error(request, "Erro ao atualizar o perfil. Verifique os dados.")

    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, 'usuarios/perfil.html', {'form': form, 'pagina_atual': 'perfil'})


def user_login(request):
    if request.user.is_authenticated:
        print("🔄 Usuário já autenticado. Redirecionando para chat...")
        return redirect('chat')

    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username_or_cnpj = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username_or_cnpj, password=password)
            if user:
                login(request, user)

                # 🔹 Salvar o idioma na sessão após login
                idioma_preferido = getattr(user, "idioma", "en")
                request.session["user_language"] = idioma_preferido
                activate(idioma_preferido)

                print(f"✅ Usuário autenticado com sucesso: {user.username}, idioma: {idioma_preferido}")

                # 🔹 Imprime antes de redirecionar
                redirect_url = request.GET.get('next') or 'chat'
                print(f"🔄 Redirecionando para: {redirect_url}")

                return redirect(redirect_url)  # 🔥 Isso precisa retornar `302` no log!

            else:
                print("❌ Erro de login: Usuário ou senha inválidos.")
                messages.error(request, "Usuário ou CNPJ e senha inválidos.")

    else:
        form = CustomLoginForm()

    return render(request, 'usuarios/login.html', {'form': form})



logger = logging.getLogger(__name__)  # Criando o logger para registrar eventos



def formatar_texto_para_html(texto):
    """Converte Markdown para HTML antes de exibir a resposta no chat."""
    if not texto:
        return ""

    html_formatado = markdown.markdown(
        texto,
        extensions=['extra', 'tables', 'fenced_code']  # 🔥 Garante suporte para tabelas!
    )

    return mark_safe(html_formatado)  # Evita escapar HTML válido no Django



@login_required 
def chat(request):
    session_id = request.GET.get('session')
    session = get_object_or_404(ChatSession, id=session_id, user=request.user) if session_id else \
              ChatSession.objects.filter(user=request.user).order_by('-created_at').first()

    if not session:
        return redirect('nova_conversa')

    chat_history = ChatHistory.objects.filter(session=session).order_by('timestamp')
    chat_history_formatado = [
        {"question": msg.question, "answer": msg.answer}
        for msg in chat_history
        if "não consegui gerar uma resposta precisa" not in msg.answer.lower()
    ]

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        uploaded_file = request.FILES.get('file')

        if not user_message and not uploaded_file:
            return JsonResponse({"success": False, "message": "A mensagem não pode estar vazia."})

        file_path = None
        contexto_adicional = None
        limpar_contexto = False  # 🧠 Para resetar histórico se novo arquivo enviado

        if uploaded_file:
            file_path = os.path.join(settings.MEDIA_ROOT, "uploads", uploaded_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            if uploaded_file.name.lower().endswith('.pdf'):
                extracted_text = processar_arquivo(file_path)
                if extracted_text:
                    contexto_adicional = f"[Texto extraído do PDF]:\n{extracted_text}"
                    limpar_contexto = True  # ⚠️ Zera o histórico se for novo arquivo

        # Define título da sessão
        if not session.title or session.title == "Nova Conversa":
            session.title = user_message[:45] if user_message else "Nova Conversa"
            session.save()

        if "resumo" in user_message.lower() or "resuma" in user_message.lower():
            ultima_resposta = recuperar_ultima_resposta(request.user)
            if ultima_resposta:
                prompt_resumo = f"Resuma o seguinte texto de forma objetiva:\n\n{ultima_resposta}"
                ai_response = processar_comunicacao_multi_ia(prompt_resumo, chat_history_formatado)
            else:
                ai_response = "Não há texto anterior para resumir."
        else:
            # 🔁 Prompt automático se não há mensagem
            if not user_message and contexto_adicional:
                user_message = (
                    f"O usuário enviou um documento com o seguinte conteúdo:\n\n"
                    f"{contexto_adicional[:800]}\n\n"
                    f"Com base nesse conteúdo, forneça um resumo ou destaque os principais pontos."
                )
            elif not user_message:
                user_message = "O usuário enviou um arquivo e deseja informações sobre o conteúdo."

            # ✅ Cache por JSON (somente se não for novo PDF)
            if not limpar_contexto:
                conhecimento = carregar_conhecimento()
                contexto_json = buscar_no_json(user_message, conhecimento)

                if contexto_json and (not session.contexto_usado or contexto_json not in session.contexto_usado):
                    contexto_adicional = (contexto_adicional or "") + "\n\n" + contexto_json
                    session.contexto_usado = (session.contexto_usado or "") + "\n\n" + contexto_json
                    session.save()
                    logger.debug("[CACHE] Contexto do JSON adicionado à sessão.")
                else:
                    logger.debug("[CACHE] Contexto já utilizado anteriormente ou não encontrado.")

            ai_response = gerar_resposta(
                user_message,
                [] if limpar_contexto else chat_history_formatado,
                file_path,
                contexto_adicional
            )

            if not ai_response or "não consegui gerar uma resposta precisa" in ai_response.lower():
                ai_response = processar_comunicacao_multi_ia(user_message, chat_history_formatado)

            if not ai_response or "não consegui gerar uma resposta precisa" in ai_response.lower():
                ai_response = processar_comunicacao_multi_ia(user_message, [])

            if not ai_response:
                ai_response = "Desculpe, não consegui processar sua mensagem."

        resposta_formatada_html = formatar_texto_para_html(ai_response)

        ChatHistory.objects.create(
            session=session,
            user=request.user,
            question=user_message or "[Arquivo enviado]",
            answer=resposta_formatada_html,
            file_name=uploaded_file.name if uploaded_file else None
        )

        return JsonResponse({"response": resposta_formatada_html})

    return render(request, 'usuarios/chat.html', {
        'chat_history': chat_history,
        'sessions': ChatSession.objects.filter(user=request.user).order_by('-created_at'),
        'current_session': session,
        'pagina_atual': 'chat'
    })






# ✅ Função para extrair texto de um PDF
def extract_text_from_pdf(file_path):
    """Extrai o texto de um arquivo PDF."""
    try:
        with fitz.open(file_path) as pdf:
            text = ""
            for page in pdf:
                text += page.get_text("text") + "\n"
        return text.strip() if text else "O PDF não contém texto extraível."
    except Exception as e:
        print(f"[ERROR] Erro ao extrair texto do PDF: {e}")
        return "Erro ao processar o PDF."
    

def handle_uploaded_file(uploaded_file):
    """Salva o arquivo no diretório de uploads"""
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    os.makedirs(upload_dir, exist_ok=True)  # ✅ Garante que o diretório existe

    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return settings.MEDIA_URL + f"uploads/{uploaded_file.name}"





def definir_idioma(request):
    if request.method == "POST":
        novo_idioma = request.POST.get("idioma")
        if novo_idioma in ["en", "pt", "es"]:  # Idiomas suportados
            request.session["user_language"] = novo_idioma
            return JsonResponse({"status": "Idioma atualizado", "idioma": novo_idioma})
        return JsonResponse({"status": "Erro", "mensagem": "Idioma não suportado"}, status=400)
    return JsonResponse({"status": "Método não permitido"}, status=405)



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





def logout_view(request):
    """Efetua logout do usuário e redireciona para a página inicial."""
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('home')



#

@login_required
def nova_conversa(request):
    
    ultima_sessao = ChatSession.objects.filter(user=request.user).order_by('-created_at').first()
    if ultima_sessao and not ChatHistory.objects.filter(session=ultima_sessao).exists():
        # Redireciona para a sessão existente se estiver "vazia"
        return redirect(f"/chat/?session={ultima_sessao.id}")

    
    new_session = ChatSession.objects.create(user=request.user, title="Nova Conversa")
    return redirect(f"/chat/?session={new_session.id}")



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
def deletar_conta(request):
    """Exclui a conta do usuário logado."""
    user = request.user
    user.delete()
    messages.success(request, "Sua conta foi excluída com sucesso.")
    return redirect('home')



def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            # Gerar código de verificação
            code_instance, created = PasswordResetCode.objects.get_or_create(user=user)
            code_instance.generate_code()
            code_instance.save()

            # Enviar código por e-mail
            subject = "Código de Redefinição de Senha - QuickEAM"
            message = f"Seu código de verificação para redefinir a senha é: {code_instance.code}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            return JsonResponse({"success": True, "message": "Código de verificação enviado para seu e-mail."})

        return JsonResponse({"success": False, "message": "Nenhuma conta encontrada com este e-mail."})

    return render(request, "usuarios/password_reset.html", {'pagina_atual': 'password_reset_request'})

def validate_reset_code(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        code = request.POST.get("code", "").strip()

        if not email:
            return JsonResponse({"success": False, "message": "E-mail não informado."})

        if not code:
            return JsonResponse({"success": False, "message": "Código não informado."})

        user = User.objects.filter(email=email).first()

        if user:
            code_instance = PasswordResetCode.objects.filter(user=user).first()

            if code_instance:
                stored_code = code_instance.code.strip()
                
                if stored_code == code:
                    if code_instance.is_expired():
                        code_instance.delete()
                        return JsonResponse({"success": False, "message": "Código expirado! Solicite um novo."})

                    return JsonResponse({"success": True, "message": "Código válido! Agora redefina sua senha."})

        return JsonResponse({"success": False, "message": "Código inválido ou expirado."})

    return JsonResponse({"success": False, "message": "Requisição inválida."})

def password_reset_confirm(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        code = request.POST.get("code", "").strip()
        new_password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if not email:
            return JsonResponse({"success": False, "message": "E-mail não informado."})

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"success": False, "message": "Usuário não encontrado."})

        code_instance = PasswordResetCode.objects.filter(user=user, code=code).first()
        if not code_instance:
            return JsonResponse({"success": False, "message": "Código inválido."})

        if code_instance.is_expired():
            code_instance.delete()
            return JsonResponse({"success": False, "message": "Código expirado! Solicite um novo."})

        if new_password != confirm_password:
            return JsonResponse({"success": False, "message": "As senhas não coincidem."})

        try:
            SenhaPersonalizada().validate(new_password)
        except ValidationError as e:
            return JsonResponse({"success": False, "message": "Senha inválida: " + " ".join(e.messages)})

        user.set_password(new_password)
        user.save()
        code_instance.delete()

        return JsonResponse({
            "success": True,
            "message": "Senha redefinida com sucesso!",
            "redirect_url": reverse("login")
        })

    return JsonResponse({"success": False, "message": "Requisição inválida."})



def listar_categorias(request):
    idioma = request.session.get('user_language', 'en')  # Obtém o idioma da sessão (ex: "en", "pt", "es")

    try:
        categorias = Categoria.objects.prefetch_related("traducoes").all()
    except DatabaseError as e:
        messages.error(request, f"Erro ao acessar categorias: {e}")
        categorias = []  # Se der erro, evita quebra e retorna lista vazia

    categorias_formatadas = []
    for categoria in categorias:
        try:
            traducao = categoria.traducoes.filter(cod_idioma=idioma).first()
            descricao = traducao.descricao if traducao else categoria.descricao
        except AttributeError:
            descricao = categoria.descricao  # Se der erro, usa a descrição original
        
        categorias_formatadas.append({
            "cod_categoria": categoria.cod_categoria,
            "descricao": descricao,
            "cod_categoria_pai": categoria.cod_categoria_pai.cod_categoria if categoria.cod_categoria_pai else None
        })

    return render(request, "gpp/listar_categorias.html", {"categorias": categorias ,'pagina_atual': 'listar_categorias'})




# 🔹 Criar Categoria
def criar_categoria(request):
    categorias_existentes = Categoria.objects.all()  # 🔹 Obtém todas as categorias existentes

    if request.method == "POST":
        descricao = request.POST.get("descricao")
        idioma = request.POST.get("idioma", "pt")  # Padrão para português
        categoria_pai_id = request.POST.get("categoria_pai")  # 🔹 Obtém a categoria pai selecionada

        if descricao:
            # Gera um código único baseado na contagem total de categorias + 1
            ultimo_codigo = Categoria.objects.order_by('-cod_categoria').first()
            if ultimo_codigo:
                num = int(ultimo_codigo.cod_categoria.replace("CAT", "")) + 1
            else:
                num = 1  # Se não houver categorias, inicia a contagem do zero

            novo_cod_categoria = f"CAT{num}"

            # Criar a categoria
            categoria = Categoria.objects.create(
                cod_categoria=novo_cod_categoria,
                descricao=descricao
            )

            # Se houver categoria pai selecionada, vincular
            if categoria_pai_id:
                categoria.cod_categoria_pai = Categoria.objects.get(cod_categoria=categoria_pai_id)
                categoria.save()

            # Criar a tradução correspondente
            CategoriaLang.objects.create(
                cod_categoria=categoria,
                cod_idioma=idioma,
                descricao=descricao
            )

        return redirect("listar_categorias")

    return render(request, "gpp/criar_categoria.html", {
        "categorias": categorias_existentes  # 🔹 Agora passamos as categorias para o template
    })



# 🔹 Editar Categoria
def editar_categoria(request, cod_categoria):
    categoria = get_object_or_404(Categoria, cod_categoria=cod_categoria)
    
    if request.method == "POST":
        # Atualiza a descrição da categoria
        categoria.descricao = request.POST.get("descricao")

        # Atualiza a categoria pai
        categoria_pai_id = request.POST.get("categoria_pai")
        if categoria_pai_id:
            categoria.cod_categoria_pai = Categoria.objects.get(cod_categoria=categoria_pai_id)
        else:
            categoria.cod_categoria_pai = None  # Define como raiz

        categoria.save()

        # 🔹 Pegamos as traduções existentes no banco
        traducoes_existentes = list(categoria.traducoes.all().values_list("id", flat=True))

        # 🔹 Pegamos os IDs das traduções enviadas pelo formulário
        traducoes_ids = request.POST.getlist("traducoes_ids[]")  # ID das traduções existentes
        idiomas = request.POST.getlist("idiomas[]")  # Lista de idiomas enviados
        traducoes = request.POST.getlist("traducoes[]")  # Lista de descrições enviadas

        traducoes_ids = [int(id) for id in traducoes_ids if id]  # Convertendo IDs válidos para inteiros
        
        # 🔹 Excluir traduções que não estão mais na lista enviada pelo formulário
        for traducao_id in traducoes_existentes:
            if traducao_id not in traducoes_ids:
                CategoriaLang.objects.filter(id=traducao_id).delete()  # Deletar traduções removidas no frontend

        # 🔹 Atualizar ou Criar novas traduções
        for i in range(len(idiomas)):
            if i < len(traducoes_ids) and traducoes_ids[i]:  # Atualizar tradução existente
                trad = CategoriaLang.objects.get(id=traducoes_ids[i])
                trad.cod_idioma = idiomas[i]
                trad.descricao = traducoes[i]
                trad.save()
            else:  # Criar nova tradução
                CategoriaLang.objects.create(
                    cod_categoria=categoria,
                    cod_idioma=idiomas[i],
                    descricao=traducoes[i]
                )

        return redirect("listar_categorias")

    categorias = Categoria.objects.exclude(cod_categoria=categoria.cod_categoria)

    return render(request, "gpp/editar_categoria.html", {
        "categoria": categoria,
        "categorias": categorias
    })




def adicionar_traducao(request, cod_categoria):
    categoria = get_object_or_404(Categoria, cod_categoria=cod_categoria)

    if request.method == "POST":
        idioma = request.POST.get("idioma").strip()
        descricao_traduzida = request.POST.get("descricao_traduzida").strip()

        if idioma and descricao_traduzida:
            # Verifica se a tradução já existe
            traducao_existente = CategoriaLang.objects.filter(
                cod_categoria=categoria,
                cod_idioma=idioma
            ).first()

            if traducao_existente:
                messages.error(request, f"A tradução para {idioma.upper()} já existe!")
            else:
                CategoriaLang.objects.create(
                    cod_categoria=categoria,
                    cod_idioma=idioma,
                    descricao=descricao_traduzida
                )
                messages.success(request, f"Tradução para {idioma.upper()} adicionada com sucesso!")

    return redirect("editar_categoria", cod_categoria=categoria.cod_categoria)



# 🔹 Excluir Categoria (SEM JAVASCRIPT, APENAS FORMULÁRIO)
def excluir_categoria(request, cod_categoria):
    categoria = get_object_or_404(Categoria, cod_categoria=cod_categoria)

    # ✅ Se a categoria tem subcategorias, impedimos a exclusão direta
    if Categoria.objects.filter(cod_categoria_pai=categoria).exists():
        messages.error(request, "Não é possível excluir uma categoria que tenha subcategorias. Remova as subcategorias primeiro.")
        return redirect("listar_categorias")

    # ✅ Exclui apenas as traduções da categoria específica
    categoria.traducoes.all().delete()

    # ✅ Agora, exclui a categoria corretamente
    categoria.delete()

    messages.success(request, "Categoria excluída com sucesso!")
    return redirect("listar_categorias")

        


# 🔹 Listar Especialidades
def listar_especialidades(request):
    filtro = request.GET.get('filtro', 'todas')  # Obtém o filtro da URL
    if filtro == 'ativas':
        especialidades = Especialidade.objects.filter(ativo=True)
    elif filtro == 'inativas':
        especialidades = Especialidade.objects.filter(ativo=False)
    else:
        especialidades = Especialidade.objects.all()
    
    return render(request, 'gpp/listar_especialidades.html', {'especialidades': especialidades, 'filtro': filtro ,'pagina_atual': 'listar_especialidades'})




def alterar_status_especialidade(request, id):
    especialidade = get_object_or_404(Especialidade, cod_especialidade=id)
    especialidade.ativo = not especialidade.ativo  # Inverte o status
    especialidade.save()
    messages.success(request, f"Especialidade {especialidade.descricao} {'ativada' if especialidade.ativo else 'desativada'}.")
    return redirect('listar_especialidades')



# 🔹 Criar Especialidade
def criar_especialidade(request):
    if request.method == "POST":
        descricao = request.POST.get("descricao")
        
        if descricao:
            # Gera código automático
            ultimo_codigo = Especialidade.objects.order_by('-cod_especialidade').first()
            if ultimo_codigo:
                num = int(ultimo_codigo.cod_especialidade.replace("ESP", "")) + 1
            else:
                num = 1

            novo_cod_especialidade = f"ESP{num}"

            Especialidade.objects.create(
                cod_especialidade=novo_cod_especialidade,
                descricao=descricao
            )

        return redirect("listar_especialidades")
    
    return render(request, "gpp/criar_especialidade.html")


# 🔹 Editar Especialidade
def editar_especialidade(request, cod_especialidade):
    especialidade = get_object_or_404(Especialidade, cod_especialidade=cod_especialidade)
    
    if request.method == "POST":
        especialidade.descricao = request.POST.get("descricao")
        especialidade.save()
        return redirect("listar_especialidades" )

    return render(request, "gpp/editar_especialidade.html", {"especialidade": especialidade, 'pagina_atual': 'listar_especialidades' })



# 🔹 Listar Ciclos de Manutenção
def listar_ciclos(request):
    query = request.GET.get("q")

    if query:
        ciclos = CicloManutencao.objects.filter(
            descricao__icontains=query
        ) | CicloManutencao.objects.filter(
            cod_ciclo__icontains=query
        )
    else:
        ciclos = CicloManutencao.objects.all()

    return render(request, "gpp/listar_ciclos.html", {
        "ciclos": ciclos,
        "pagina_atual": "listar_ciclos"
    })



# 🔹 Criar Ciclo de Manutenção
@login_required
def criar_ciclo(request):
    categorias = Categoria.objects.all()  # Busca todas as categorias
    especialidades = Especialidade.objects.all()  # Busca todas as especialidades

    if request.method == "POST":
        form = CicloPadraoForm(request.POST)
        if form.is_valid():
            # 🔹 Gera automaticamente o código do ciclo baseado no último ciclo cadastrado
            ultimo_ciclo = CicloManutencao.objects.order_by('-cod_ciclo').first()
            if ultimo_ciclo:
                num = int(ultimo_ciclo.cod_ciclo.replace("CICLO", "")) + 1
            else:
                num = 1  # Se não houver ciclos cadastrados, começa do 1

            novo_cod_ciclo = f"CICLO{num}"

            # 🔹 Salva o novo ciclo com o código gerado
            ciclo = form.save(commit=False)
            ciclo.cod_ciclo = novo_cod_ciclo
            ciclo.save()
            messages.success(request, "Ciclo criado com sucesso!")
            return redirect('listar_ciclos')
    else:
        form = CicloPadraoForm()

    return render(request, "gpp/criar_ciclos.html", {
        "form": form,
        "categorias": categorias,
        "especialidades": especialidades,
    })




# 🔹 Editar Ciclo de Manutenção
def editar_ciclo(request, cod_ciclo):
    ciclo = get_object_or_404(CicloManutencao, cod_ciclo=cod_ciclo)

    if request.method == "POST":
        form = CicloPadraoForm(request.POST, instance=ciclo)
        if form.is_valid():
            form.save()
            return redirect('listar_ciclos')  # Redireciona para a listagem de ciclos após a edição
    else:
        form = CicloPadraoForm(instance=ciclo)  # Preenche o formulário com os dados do ciclo

    return render(request, "gpp/editar_ciclo.html", {"form": form, "ciclo": ciclo})




# 🔹 Excluir Ciclo de Manutenção
def excluir_ciclo(request, cod_ciclo):
    ciclo = get_object_or_404(CicloManutencao, cod_ciclo=cod_ciclo)
    ciclo.delete()
    messages.success(request, "Ciclo excluído com sucesso!")
    return redirect('listar_ciclos')


def listar_matriz(request):
    query = request.GET.get("q")
    if query:
        matriz = MatrizPadraoAtividade.objects.filter(
            descricao__icontains=query
        )
    else:
        matriz = MatrizPadraoAtividade.objects.all()

    return render(request, "gpp/listar_matriz.html", {"matriz": matriz, "pagina_atual": "listar_matriz"})




def criar_matriz(request):
    if request.method == "POST":
        form = MatrizPadraoAtividadeForm(request.POST)
        if form.is_valid():
            # 🔹 Gera automaticamente o código da matriz
            ultimo_matriz = MatrizPadraoAtividade.objects.order_by('-cod_matriz').first()
            if ultimo_matriz:
                num = int(ultimo_matriz.cod_matriz.replace("MATRIZ", "")) + 1
            else:
                num = 1

            novo_cod_matriz = f"MATRIZ{num}"

            # 🔹 Salva o novo registro
            matriz = form.save(commit=False)
            matriz.cod_matriz = novo_cod_matriz
            matriz.save()
            return redirect('listar_matriz')
    else:
        form = MatrizPadraoAtividadeForm()

    return render(request, "gpp/criar_matriz.html", {"form": form})


def editar_matriz(request, id):
    matriz = get_object_or_404(MatrizPadraoAtividade, cod_matriz=id)

    if request.method == "POST":
        form = MatrizPadraoAtividadeForm(request.POST, instance=matriz)
        if form.is_valid():
            form.save()
            messages.success(request, "Relação atualizada com sucesso!")
            return redirect('listar_matriz')
    else:
        form = MatrizPadraoAtividadeForm(instance=matriz)  # 🟢 Verifique se os dados estão corretos

    return render(request, 'gpp/editar_matriz.html', {'form': form, 'matriz': matriz})


def excluir_matriz(request, id):
    matriz = get_object_or_404(MatrizPadraoAtividade, cod_matriz=id)
    matriz.delete()
    messages.success(request, "Relação excluída com sucesso!")
    return redirect('listar_matriz')