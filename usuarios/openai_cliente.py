import openai
import os
from dotenv import load_dotenv, find_dotenv
_= load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_resposta_openai(user_message, contexto=None):
    if contexto is None:
        contexto = []

    # Converta o contexto de dicionário para lista de mensagens, se necessário
    if isinstance(contexto, dict):
        contexto = [
            {"role": "assistant", "content": f"Llama: {contexto.get('Llama', '')}"},
            {"role": "assistant", "content": f"Gemini: {contexto.get('Gemini', '')}"}
        ]

    try:
        # Combine o contexto com a mensagem do usuário
        messages = contexto + [{"role": "user", "content": user_message}]

        # Chamada para a API da OpenAI
        response = openai.ChatCompletion.create(
            model="chatgpt-4o-latest",
            messages=messages,
            temperature=0.7,
            max_tokens=150,
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Erro na API OpenAI: {e}")
        return "Desculpe, ocorreu um erro ao processar sua mensagem."