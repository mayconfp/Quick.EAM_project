from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
from .models import ChatHistory
import json

def processar_comunicacao_multi_ia(mensagem, historico=None):
    try:
        # Log da mensagem recebida
        print(f"[DEBUG] Mensagem recebida para processar: {mensagem}")
        if historico:
            print(f"[DEBUG] Histórico recebido: {list(historico)}")

        # Inicializar dicionário para armazenar respostas de cada IA
        respostas_adicionais = {
            "Llama": None,
            "Gemini": None,
            "Historico": [msg.question for msg in historico] if historico else []
        }

        # Obter resposta da Llama
        try:
            resposta_llama = gerar_resposta_llama(mensagem)
            respostas_adicionais["Llama"] = resposta_llama
            print(f"[DEBUG] Resposta da Llama: {resposta_llama}")
        except Exception as e:
            print(f"[ERROR] Erro ao obter resposta da Llama: {e}")
            respostas_adicionais["Llama"] = "Erro ao processar com Llama."

        # Obter resposta da Gemini
        try:
            resposta_gemini = gemini_gerar_resposta(mensagem)
            respostas_adicionais["Gemini"] = resposta_gemini
            print(f"[DEBUG] Resposta da Gemini: {resposta_gemini}")
        except Exception as e:
            print(f"[ERROR] Erro ao obter resposta da Gemini: {e}")
            respostas_adicionais["Gemini"] = "Erro ao processar com Gemini."

        # Preparar contexto para OpenAI
        print(f"[DEBUG] Contexto enviado para OpenAI: {respostas_adicionais}")

        # Obter resposta final da OpenAI
        resposta_final = gerar_resposta_openai(mensagem, respostas_adicionais)
        print(f"[DEBUG] Resposta final da OpenAI: {resposta_final}")

        # Certificar-se de que a resposta está em formato JSON e codificada corretamente
        return json.dumps(resposta_final, ensure_ascii=False)

    except Exception as e:
        print(f"[ERROR] Erro ao processar comunicação multi-IA: {e}")
        return json.dumps({"erro": "Erro ao processar as respostas entre as IAs."}, ensure_ascii=False)

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