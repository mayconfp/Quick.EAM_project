from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
import logging
from .models import ChatHistory
from .openai_cliente import processar_arquivo
from .openai_cliente import carregar_conhecimento
from .openai_cliente import buscar_no_json
from .openai_cliente import buscar_no_json, carregar_conhecimento, gerar_resposta_openai, processar_arquivo
import os
import fitz

logger = logging.getLogger(__name__)


def gerar_resposta(user_message, chat_history=None, file_path=None, contexto_adicional=None):
    """Gera uma resposta consolidada com base no JSON, arquivos e IA."""
    if not isinstance(user_message, str) or not user_message.strip():
        logger.warning("Mensagem inválida recebida.")
        return "Não entendi sua mensagem. Pode reformular?"

    user_message = user_message.strip()

    # Busca no JSON e adiciona ao contexto
    contexto_json = buscar_no_json(user_message, carregar_conhecimento())
    if contexto_json:
        contexto_adicional = (contexto_adicional or "") + "\n\n" + contexto_json

    # Processa o arquivo PDF
    extracted_text = processar_arquivo(file_path) if file_path else None
    if extracted_text:
        contexto_adicional = (contexto_adicional or "") + f"\n\n[Conteúdo do PDF]:\n{extracted_text}"

    return gerar_resposta_openai(user_message, chat_history, contexto_adicional) or \
           "Desculpe, não consegui processar sua mensagem. Tente reformular."





def processar_comunicacao_multi_ia(user_message, historico):
    """Processa a mensagem consultando JSON antes de usar IAs externas."""

    if not user_message.strip():
        return "A mensagem não pode estar vazia."

    # 🔎 **Verifica se é um pedido de resumo**
    if "resuma" in user_message.lower() or "resumo" in user_message.lower():
        return gerar_resposta(user_message, [])  # Remove contexto da QuickEAM

    respostas = {}

    try:
        respostas['openai'] = gerar_resposta(user_message, historico)
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
