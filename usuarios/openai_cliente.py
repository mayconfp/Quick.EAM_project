import openai
import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_resposta_openai(user_message, contexto=None):
    if contexto is None:
        contexto = []

    try:
        messages = contexto + [{"role": "user", "content": user_message}]
        response = openai.ChatCompletion.create(
            model="chatgpt-4o-latest",
            messages=messages,
            temperature=0.7,
            max_tokens=700,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Erro na API OpenAI: {e}")
        return "Erro ao processar a mensagem com a OpenAI."
