from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
from .models import ChatHistory


def processar_comunicacao_multi_ia(mensagem, historico=None):
    """
    Processa a mensagem com as 3 IAs e retorna uma resposta final da OpenAI.
    """
    try:
        print(f"[DEBUG] Mensagem recebida para processar: {mensagem}")

        # Obter resposta da Llama
        resposta_llama = gerar_resposta_llama(mensagem)
        print(f"[DEBUG] Resposta da Llama: {resposta_llama}")

        # Obter resposta da Gemini
        resposta_gemini = gemini_gerar_resposta(mensagem)
        print(f"[DEBUG] Resposta da Gemini: {resposta_gemini}")

        # Criar o contexto inicial com respostas das outras IAs
        contexto = []
        if historico:
            contexto.extend([
                {"role": "user", "content": chat.question} if chat.question else {"role": "assistant", "content": chat.answer}
                for chat in historico
            ])

        contexto.extend([
            {"role": "assistant", "content": f"Llama disse: {resposta_llama}"},
            {"role": "assistant", "content": f"Gemini disse: {resposta_gemini}"}
        ])

        # Obter resposta final da OpenAI
        print(f"[DEBUG] Contexto enviado para OpenAI: {contexto}")
        resposta_final = gerar_resposta_openai(mensagem, contexto)
        print(f"[DEBUG] Resposta final da OpenAI: {resposta_final}")

        return resposta_final

    except Exception as e:
        print(f"[ERROR] Erro ao processar comunicação multi-IA: {e}")
        return "Erro ao processar as respostas entre as IAs."