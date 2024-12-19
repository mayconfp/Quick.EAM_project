from .provedores import gerar_resposta
from .models import ChatHistory


def processar_pergunta_com_respostas(user_message, user):
    """
    Consulta outras IAs (Llama, Gemini), combina as respostas e retorna a resposta final da OpenAI.

    Inclui o histórico recente no contexto para que a IA entenda o que deve ser resumido.
    """
    provedores = ['llama', 'gemini']  # IAs auxiliares
    respostas_auxiliares = {}

    # Recupera o histórico recente do usuário
    historico = ChatHistory.objects.filter(user=user).order_by('-timestamp')[:5]  # Últimas 5 mensagens
    historico_formatado = formatar_historico_para_contexto(historico)

    # Consulta as IAs auxiliares
    for provedor in provedores:
        try:
            resposta = gerar_resposta(provedor, user_message)
            respostas_auxiliares[provedor] = resposta
        except Exception as e:
            respostas_auxiliares[provedor] = f"Erro ao obter resposta do {provedor}: {e}"

    # Cria o contexto com as respostas das IAs auxiliares e o histórico
    contexto = formatar_contexto_para_ia(user_message, respostas_auxiliares, historico_formatado)

    # Consulta a OpenAI com o contexto
    try:
        resposta_final = gerar_resposta('openai', contexto)
    except Exception as e:
        resposta_final = f"Erro ao obter resposta da OpenAI: {e}"

    return resposta_final


def formatar_historico_para_contexto(historico):
    """
    Formata o histórico de mensagens para ser incluído no contexto.
    """
    contexto = "Histórico de conversa:\n"
    for chat in reversed(historico):  # Inverte a ordem para exibir do mais antigo para o mais recente
        contexto += f"Você: {chat.question}\n"
        contexto += f"Manuela: {chat.answer}\n"
    return contexto


def formatar_contexto_para_ia(user_message, respostas_auxiliares, historico_formatado):
    """
    Formata as respostas das IAs auxiliares e o histórico como contexto para a OpenAI.
    """
    contexto = historico_formatado  # Adiciona o histórico formatado
    contexto += f"\nPergunta do usuário: {user_message}\n\n"
    contexto += "Aqui estão as respostas de outras inteligências artificiais:\n"

    for provedor, resposta in respostas_auxiliares.items():
        contexto += f"- Resposta de {provedor.capitalize()}: {resposta}\n"

    contexto += "\nCom base nessas informações, forneça a melhor resposta possível."
    return contexto
