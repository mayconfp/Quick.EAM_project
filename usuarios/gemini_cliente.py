import os
import requests
from dotenv import load_dotenv, find_dotenv

# Carrega variáveis do arquivo ..env
load_dotenv(find_dotenv())

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")

def gemini_gerar_respota(user_message):
    # Envia uma mensagem para a API Gemini e retorna a resposta gerada.
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"  # Monta a URL com a chave API

    headers = {
        'Content-Type': 'application/json',
    }

    payload = {
        "contents": [
            {"parts": [{"text": user_message}]}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Verifica erros HTTP

        # Processa a resposta para pegar o texto
        response_data = response.json()
        candidates = response_data.get('candidates', [{}])

        # Acessa o texto dentro do caminho correto
        content_parts = candidates[0].get('content', {}).get('parts', [])
        if content_parts:
            return content_parts[0].get('text', 'Sem resposta gerada.')

        return "Sem resposta gerada pela IA Gemini."
    except (requests.RequestException, IndexError, KeyError) as e:
        print(f"Erro ao acessar ou processar a API Gemini: {e}")
        return "Erro ao se comunicar com a IA Gemini."
