from .models import ChatHistory
from .provedores import gerar_resposta

def process_chat_message(user, user_message, provedor):
    """
    Processa uma mensagem de chat com o provedor especificado.
    """
    if not user_message:
        return None

    try:
        # Gera a resposta do provedor correto
        ai_response = gerar_resposta(provedor, user_message)

        # Salva no histórico
        ChatHistory.objects.create(
            user=user,
            question=user_message,
            answer=ai_response,
            ia_used=provedor
        )
        return ai_response

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return "Erro ao processar sua mensagem."
