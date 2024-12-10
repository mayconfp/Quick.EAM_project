import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_resposta(mensagem_usuario):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Modelo usado
            messages=[{"role": "user", "content": mensagem_usuario}]
        )
        return resposta['choices'][0]['message']['content']
    except Exception as e:
        return f"Erro ao se comunicar com a IA: {str(e)}"
