import os
from llamaapi import LlamaAPI

LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
llama = LlamaAPI(LLAMA_API_KEY)

def gerar_resposta_llama(mensagem_usuario):
    api_request_json = {
        "model": "llama3.1-70b",
        "messages": [{"role": "user", "content": mensagem_usuario}],
        "stream": False,
        "temperature": 0.5,
    }

    try:
        print(f"[DEBUG] Enviando requisição para o Llama API com a mensagem: {mensagem_usuario}")

        # Faz a requisição à API do Llama
        response = llama.run(api_request_json)
        print(f"[DEBUG] Resposta recebida da Llama API: {response}")

        # Processa o JSON retornado pela API
        result = response.json()
        print(f"[DEBUG] Resultado processado da Llama API: {result}")

        # Verifica se a estrutura da resposta é válida
        if "choices" in result and result["choices"]:
            resposta = result["choices"][0]["message"]["content"]
            print(f"[DEBUG] Resposta extraída: {resposta}")
            return resposta.strip()
        else:
            print("[ERROR] Estrutura da resposta da API do Llama está incompleta ou incorreta.")
            return "Erro: Resposta inválida ou incompleta da Llama API."

    except KeyError as ke:
        print(f"[ERROR] Chave ausente na resposta da API do Llama: {ke}")
        return "Erro ao processar a resposta da Llama API. Detalhes da estrutura não encontrados."
    except Exception as e:
        print(f"[ERROR] Erro ao se comunicar com a API do Llama: {e}")
        return "Erro ao processar sua mensagem com o Llama API."
