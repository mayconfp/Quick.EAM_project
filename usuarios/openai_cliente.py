import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

from openai import ChatCompletion  # Certifique-se de usar sua configuração da OpenAI

def gerar_resposta_openai(mensagem, respostas_adicionais=None):
    """
    Gera uma resposta do OpenAI, considerando respostas adicionais de outras IAs.
    """
    mensagens = [{"role": "user", "content": mensagem}]

    if respostas_adicionais:
        for resposta in respostas_adicionais:
            mensagens.append({"role": "assistant", "content": resposta})

    try:
        response = ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=mensagens,
            temperature=0.5
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro com OpenAI: {e}")
        return "Erro ao processar resposta da OpenAI."
