from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
from .models import ChatHistory

def processar_comunicacao_multi_ia(mensagem):
    """
    Processa a mensagem com as 3 IAs, mas apenas a OpenAI sintetiza a resposta final.
    """
    try:
        print(f"[DEBUG] Mensagem recebida para processar: {mensagem}")

        # Obter resposta da Llama
        resposta_llama = gerar_resposta_llama(mensagem)
        print(f"[DEBUG] Resposta da Llama: {resposta_llama}")

        # Obter resposta da Gemini
        resposta_gemini = gemini_gerar_resposta(mensagem)
        print(f"[DEBUG] Resposta da Gemini: {resposta_gemini}")

        # Preparar contexto para OpenAI
        respostas_adicionais = {
            "Llama": resposta_llama,
            "Gemini": resposta_gemini,
        }
        print(f"[DEBUG] Contexto enviado para OpenAI: {respostas_adicionais}")

        # Obter resposta final da OpenAI
        resposta_final = gerar_resposta_openai(mensagem, respostas_adicionais)
        print(f"[DEBUG] Resposta final da OpenAI: {resposta_final}")

        return resposta_final

    except Exception as e:
        print(f"[ERROR] Erro ao processar comunicação multi-IA: {e}")
        return "Erro ao processar as respostas entre as IAs."


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