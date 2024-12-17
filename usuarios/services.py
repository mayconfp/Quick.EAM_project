from .provedores import gerar_resposta
from .provedores import gerar_resposta
from .models import ChatHistory

from .provedores import gerar_resposta
from .models import ChatHistory

def process_chat_message(user_message, provedor):
    """
    Processa a mensagem com base no provedor selecionado.
    """
    return f"Mensagem processada com o provedor {provedor}: {user_message}"


def processar_pergunta_com_respostas(user_message, ia_escolhida):
    """
    Consulta as outras IAs, combina suas respostas e envia o contexto à IA escolhida.

    :param user_message: Mensagem enviada pelo usuário.
    :param ia_escolhida: Provedor escolhido pelo usuário.
    :return: Resposta final da IA escolhida, com base no contexto das outras IAs.
    """
    provedores = ['openai', 'llama', 'gemini']
    respostas_auxiliares = {}

    # Remove a IA escolhida da lista de IAs auxiliares
    outros_provedores = [prov for prov in provedores if prov != ia_escolhida]

    # Consulta as IAs auxiliares
    for provedor in outros_provedores:
        try:
            resposta = gerar_resposta(provedor, user_message)
            respostas_auxiliares[provedor] = resposta
        except Exception as e:
            respostas_auxiliares[provedor] = f"Erro ao obter resposta do {provedor}: {e}"

    # Recupera o histórico recente e cria um contexto estruturado para a IA escolhida
    contexto = formatar_contexto_para_ia(user_message, respostas_auxiliares)

    # Envia o contexto para a IA escolhida
    try:
        resposta_final = gerar_resposta(ia_escolhida, contexto)
    except Exception as e:
        resposta_final = f"Erro ao obter resposta da IA escolhida ({ia_escolhida}): {e}"

    return resposta_final


def formatar_contexto_para_ia(user_message, respostas_auxiliares):
    """
    Formata o contexto para a IA escolhida, removendo referências explícitas ao histórico.
    """
    # Recupera as últimas interações do histórico
    historico = recuperar_historico_conversa()

    # Formata o contexto: histórico recente + pergunta do usuário + respostas auxiliares
    contexto = f"{historico}\n\n"
    contexto += f"Pergunta do usuário: {user_message}\n"

    for provedor, resposta in respostas_auxiliares.items():
        contexto += f"- Resposta adicional: {resposta}\n"

    # Pedido direto para a IA, sem referências explícitas ao histórico
    contexto += "\nElabore a resposta mais clara e precisa possível."
    return contexto



def recuperar_historico_conversa():
    """
    Recupera as últimas 3 interações do banco de dados.

    :return: Histórico formatado como texto.
    """
    historico = ChatHistory.objects.all().order_by('-timestamp')[:3]
    texto_historico = ""

    # Formata as interações como um texto contínuo
    for entrada in reversed(historico):
        texto_historico += f"Você: {entrada.question}\n"
        texto_historico += f"IA: {entrada.answer}\n"

    return texto_historico
