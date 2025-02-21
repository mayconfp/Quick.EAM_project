from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
import logging
from .models import ChatHistory

logger = logging.getLogger(__name__)

def gerar_resposta(user_message, chat_history=None):
    """Gera uma resposta consolidada: JSON primeiro, histórico depois, e IAs por último."""

    if not isinstance(user_message, str) or not user_message.strip():
        logger.warning("Mensagem inválida recebida.")
        return "Não entendi sua mensagem. Pode reformular?"



    user_message = user_message.strip()

    # 🔎 **Busca no JSON**
    resposta_json = gerar_resposta_openai(user_message)
    if resposta_json:
        return resposta_json  

    # 🔎 **Busca no histórico**
    if chat_history:
        for item in chat_history:
            if item.get('question', '').strip().lower() == user_message.lower():
                return item["answer"]

    # 🔎 **Se não encontrou no JSON ou no histórico, chama a IA**
    return processar_comunicacao_multi_ia(user_message, chat_history)


def processar_comunicacao_multi_ia(user_message, historico):
    """Processa a mensagem consultando JSON antes de usar IAs externas."""

    if not user_message.strip():
        return "A mensagem não pode estar vazia."

    # 🔎 **Verifica se é um pedido de resumo**
    if "resuma" in user_message.lower() or "resumo" in user_message.lower():
        return gerar_resposta_openai(user_message, [])  # Remove contexto da QuickEAM

    respostas = {}

    try:
        respostas['openai'] = gerar_resposta_openai(user_message, historico)
    except Exception as e:
        print(f"[ERROR] Erro na OpenAI: {e}")
        respostas['openai'] = None

    melhor_resposta = respostas.get('openai')

    return melhor_resposta or "Desculpe, não consegui gerar uma resposta no momento."




def recuperar_ultima_resposta(user):
    """
    Recupera a última resposta registrada no banco de dados para o usuário.
    """
    try:
        ultima_resposta = ChatHistory.objects.filter(session__user=user).order_by('-timestamp').first()
        if ultima_resposta and ultima_resposta.answer.strip():
            print(f"[DEBUG] Última resposta encontrada: {ultima_resposta.answer}")
            return ultima_resposta.answer.strip()
        else:
            print("[DEBUG] Nenhuma resposta anterior válida encontrada.")
            return None
    except Exception as e:
        print(f"[ERROR] Erro ao recuperar última resposta: {e}")
        return None
