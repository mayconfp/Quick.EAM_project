from .openai_cliente import gerar_resposta_openai, buscar_resposta_no_json
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
from .models import ChatHistory
from .provedores import processar_comunicacao_multi_ia
from .openai_cliente import carregar_conhecimento
import json


def gerar_resposta(user_message, chat_history=None):
    """Gera uma resposta consolidada do JSON e IAs."""

    # 🔎 **PASSO 1: Busca no JSON primeiro**
    resposta_json = buscar_resposta_no_json(user_message)
    if resposta_json:
        return resposta_json  # Retorna a resposta diretamente do JSON

    # 🔎 **PASSO 2: Se não estiver no JSON, busca no contexto**
    if chat_history:
        for item in chat_history:
            if user_message.lower().strip() in item['question'].lower():
                return item['answer']

    # 🔎 **PASSO 3: Se não for algo relacionado ao projeto, chama a OpenAI**
    return processar_comunicacao_multi_ia(user_message, chat_history)


def processar_comunicacao_multi_ia(mensagem, historico=None):
    try:
        print(f"[DEBUG] Mensagem recebida: {mensagem}")

        # 🔄 **Formata histórico corretamente antes de passar**
        historico_formatado = [{"question": h.question, "answer": h.answer} for h in historico] if historico else []

        # 🔎 **PASSO 1: Busca no JSON**
        resposta_json = buscar_resposta_no_json(mensagem)
        if resposta_json:
            return resposta_json

        # 🔎 **PASSO 2: Chama OpenAI**
        resposta_final = gerar_resposta_openai(mensagem, historico_formatado)
        print(f"[DEBUG] Resposta final da OpenAI: {resposta_final}")

        return resposta_final

    except Exception as e:
        print(f"[ERROR] Erro ao processar comunicação multi-IA: {e}")
        return "Erro ao processar as respostas entre as IAs."


def recuperar_ultima_resposta(user):
    """
    Recupera as última resposta registrada no banco de dados para o usuário.
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
