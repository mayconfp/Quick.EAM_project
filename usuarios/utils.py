import openai
from dotenv import load_dotenv
import os
from usuarios.models import ChatHistory, CustomUser


# Configurações de API
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def gerar_resposta(mensagem):
    """
    Gera uma resposta utilizando a API da OpenAI.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.8,
            messages=[{"role": "user", "content": mensagem}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Erro ao se comunicar com a OpenAI: {e}")
        return "Ocorreu um erro ao gerar a resposta. Tente novamente mais tarde."
