from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
import logging

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


def processar_comunicacao_multi_ia(mensagem, historico=None):
    """Processa a mensagem consultando primeiro JSON antes de usar IAs externas."""

    try:
        logger.info(f"Processando mensagem: {mensagem}")

        historico_formatado = [{"question": h.get("question"), "answer": h.get("answer")} for h in (historico or [])]

        respostas = {}

        # 🔎 **PASSO 1: Chama OpenAI**
        try:
            respostas['openai'] = gerar_resposta_openai(mensagem, historico_formatado)
        except Exception as e:
            logger.error(f"Erro na OpenAI: {e}")
            respostas['openai'] = None

        # 🔎 **PASSO 2: Se OpenAI falhar, chama Gemini**
        if not respostas['openai']:
            try:
                respostas['gemini'] = gemini_gerar_resposta(mensagem, historico_formatado)
            except Exception as e:
                logger.error(f"Erro na Gemini: {e}")
                respostas['gemini'] = None

        # 🔎 **PASSO 3: Se OpenAI e Gemini falharem, chama Llama**
        if not respostas['openai'] and not respostas['gemini']:
            try:
                respostas['llama'] = gerar_resposta_llama(mensagem, historico_formatado)
            except Exception as e:
                logger.error(f"Erro na Llama: {e}")
                respostas['llama'] = None

        # 🔥 **Retorna a melhor resposta disponível**
        melhor_resposta = respostas.get('openai') or respostas.get('gemini') or respostas.get('llama')

        return melhor_resposta or "Desculpe, não consegui gerar uma resposta para essa pergunta."

    except Exception as e:
        logger.critical(f"Erro crítico ao processar multi-IA: {e}")
        return "Ocorreu um erro inesperado ao processar sua pergunta."


def recuperar_ultima_resposta(user):
    """
    Recupera a última resposta registrada no banco de dados para o usuário.
    """
    try:
        ultima_resposta = ChatHistory.objects.filter(user=user).order_by('-timestamp').first()
        if ultima_resposta and ultima_resposta.answer.strip():
            print(f"[DEBUG] Última resposta encontrada: {ultima_resposta.answer}")
            return ultima_resposta.answer.strip()
        else:
            print("[DEBUG] Nenhuma resposta anterior válida encontrada.")
            return None
    except Exception as e:
        print(f"[ERROR] Erro ao recuperar última resposta: {e}")
        return None
