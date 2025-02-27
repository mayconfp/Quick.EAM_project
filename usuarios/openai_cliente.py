import json
import os
import openai
import difflib
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")

def carregar_conhecimento():
    """Carrega o JSON com conhecimento do projeto."""
    caminho_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "../knowledge.json"))
    try:
        with open(caminho_json, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def obter_saudacao():
    """Retorna uma saudação baseada no horário do dia."""
    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 12:
        return "Bom dia!"
    elif 12 <= hora_atual < 18:
        return "Boa tarde!"
    else:
        return "Boa noite!"

def limpar_texto(texto):
    """Remove caracteres especiais e padroniza a string para facilitar a busca."""
    return texto.lower().replace("?", "").replace("!", "").strip()

def dividir_pergunta(pergunta):
    """Separa frases compostas e retorna as partes mais relevantes."""
    delimitadores = [" e ", ", ", ". ", "; ", " mas ", " porém "]
    for d in delimitadores:
        if d in pergunta:
            return pergunta.split(d)
    return [pergunta]

def buscar_no_json(pergunta, conhecimento):
    """
    Pesquisa no JSON e retorna uma resposta caso exista algo relacionado.
    """
    pergunta_clean = limpar_texto(pergunta)
    partes = dividir_pergunta(pergunta_clean)
    
    melhor_correspondencia = None
    melhor_pontuacao = 0.0

    for parte in partes:
        for categoria, dados in conhecimento.items():
            if isinstance(dados, dict):
                for chave, valor in dados.items():
                    pontuacao = difflib.SequenceMatcher(None, parte, chave.lower()).ratio()
                    if pontuacao > melhor_pontuacao and pontuacao > 0.6:
                        melhor_correspondencia = valor
                        melhor_pontuacao = pontuacao

    return melhor_correspondencia if melhor_correspondencia else None

def gerar_resposta_openai(user_message, contexto=None):
    """
    Primeiro tenta buscar no JSON, se não encontrar, usa OpenAI para gerar uma resposta.
    """
    conhecimento = carregar_conhecimento()
    resposta_json = buscar_no_json(user_message, conhecimento)

    if resposta_json:
        return resposta_json  # ✅ Responde diretamente pelo JSON

    # Se não encontrou resposta no JSON, usa OpenAI e adiciona a base de conhecimento como contexto
    messages = [
        {"role": "system", "content": "Você é a IA Manuela, um assistente virtual especializado na empresa QuickEAM, mas também pode responder perguntas gerais sobre diversos temas."},
        {"role": "user", "content": user_message}
    ]

    # 🔥 **PASSO EXTRA: Adiciona contexto da base de conhecimento para OpenAI**
    base_conhecimento_contexto = json.dumps(conhecimento, ensure_ascii=False, indent=2)
    messages.insert(1, {"role": "system", "content": f"Aqui está a base de conhecimento da QuickEAM para referência:\n{base_conhecimento_contexto}"})

    # **Adicionar contexto ao histórico da conversa**
    if contexto:
        for item in contexto:
            messages.append({"role": "user", "content": item["question"]})
            messages.append({"role": "assistant", "content": item["answer"]})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro na API OpenAI: {e}")
        return "Não consegui processar sua pergunta no momento."

if __name__ == "__main__":
    conhecimento = carregar_conhecimento()
    
    # Teste manual de busca no JSON
    perguntas_teste = [
        "O que é a QuickEAM?",
        "Qual a missão da QuickEAM?",
        "Quem são os desenvolvedores?",
        "Quais tecnologias a QuickEAM usa?",
        "A QuickEAM faz manutenção industrial?",
        "Quais os produtos da QuickEAM?",
        "Olá tudo bem? O que é a QuickEAM?",
        "Quais ferramentas a QuickEAM usa?"
    ]
    
    for pergunta in perguntas_teste:
        resposta = gerar_resposta_openai(pergunta)
        print(f"Pergunta: {pergunta}\nResposta: {resposta}\n")
