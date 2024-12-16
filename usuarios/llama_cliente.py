import os
from llamaapi import LlamaAPI

LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
llama = LlamaAPI(LLAMA_API_KEY)

def gerar_resposta_llama(mensagem_usuario):

    api_request_json = {
        "model" : "llama3.1-70b",
        "messages": [{"role": "user", "content": mensagem_usuario}],
        "stream": False,
        "temperature":0.5,

    }

    try:
        # Faz a requisição à API do Llama
        response = llama.run(api_request_json)
        result = response.json()

        # Extrai a resposta do conteúdo retornado
        resposta = result["choices"][0]["message"]["content"]
        return resposta.strip()

    except Exception as e:
        print(f"Erro ao se comunicar com a API do Llama: {e}")
        return "Erro ao processar sua mensagem com o Llama API."
