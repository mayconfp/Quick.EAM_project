import os
from llamaapi import LlamaAPI

# Inicialize a API com o token correto
llama = LlamaAPI(api_token=os.getenv("LLAMA_API_KEY"))

def gerar_resposta_llama(user_message, contexto=None):
    if contexto is None:
        contexto = []

    api_request_json = {
        "model": "llama3.1-70b",
        "messages": contexto + [{"role": "user", "content": user_message}],
        "stream": False,
        "temperature": 0.5,
    }

    try:
        response = llama.run(api_request_json)
        result = response.json()

        if "choices" in result and result["choices"]:
            resposta = result["choices"][0]["message"]["content"]
            return resposta.strip()
        else:
            return "Erro: Resposta inválida ou incompleta da Llama API."
    except Exception as e:
        print(f"Erro ao se comunicar com a API do Llama: {e}")
        return "Erro ao processar sua mensagem com o Llama API."