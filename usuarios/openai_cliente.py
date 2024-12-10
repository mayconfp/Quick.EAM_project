from dotenv import load_dotenv, find_dotenv
import os
import openai

_=load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_resposta(mensagem_usuario):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mensagem_usuario}]
        )
        return resposta['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro ao se comunicar com a OpenAI: {e}")
        return "Ocorreu um erro ao gerar a resposta. Tente novamente mais tarde."
