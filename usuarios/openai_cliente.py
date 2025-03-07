import openai
import os
from dotenv import load_dotenv, find_dotenv
_= load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_resposta_openai(user_message, contexto=None):
    if contexto is None:
        contexto = []

    # Certifique-se de que o contexto é uma lista de dicionários
    if not isinstance(contexto, list):
        contexto = [{"role": "assistant", "content": str(contexto)}]

    try:
        # Combine o contexto com a mensagem do usuário
        messages = contexto + [{"role": "user", "content": user_message}]

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
            max_tokens=700,
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Erro na API OpenAI: {e}")
        return "Desculpe, ocorreu um erro ao processar sua mensagem."

