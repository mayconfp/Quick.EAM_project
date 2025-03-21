import json
import os
import openai
import difflib
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import fitz
import logging



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# 🔥 Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")



def processar_arquivo(file_path):
    """Extrai o texto de um arquivo e retorna seu conteúdo."""
    _, file_extension = os.path.splitext(file_path)

    if file_extension.lower() == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif file_extension.lower() == ".pdf":
        texto_extraido = []
        with fitz.open(file_path) as pdf:
            for page in pdf:
                texto_extraido.append(page.get_text())
        conteudo = " ".join(texto_extraido) if texto_extraido else None  
        if conteudo:
            return conteudo[:5000]  # 🔥 Limitamos para evitar textos muito longos

    return None  # 🔥 Retorna None caso o arquivo não possa ser processado




def carregar_conhecimento():
    """Carrega o JSON com conhecimento do projeto."""
    caminho_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "../knowledge.json"))
    try:
        with open(caminho_json, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}



def buscar_no_json(pergunta, conhecimento):
    """
    Pesquisa no JSON e retorna uma resposta sempre formatada corretamente.
    Se encontrar listas ou dicionários, transforma em texto natural.
    """
    pergunta_clean = pergunta.lower().strip()
    
    melhor_correspondencia = None
    melhor_pontuacao = 0.0

    for categoria, dados in conhecimento.items():
        if isinstance(dados, dict):
            for chave, valor in dados.items():
                pontuacao = difflib.SequenceMatcher(None, pergunta_clean, chave.lower()).ratio()
                if pontuacao > melhor_pontuacao and pontuacao > 0.6:
                    melhor_correspondencia = valor
                    melhor_pontuacao = pontuacao

    # ✅ Se a resposta for uma lista, formatamos corretamente antes de retornar
    if isinstance(melhor_correspondencia, list):
        return "Aqui estão as informações relacionadas:\n" + "\n".join(f"- {item}" for item in melhor_correspondencia)

    # ✅ Se a resposta for um dicionário, formatamos como um texto descritivo
    if isinstance(melhor_correspondencia, dict):
        resposta_formatada = "Aqui estão os detalhes:\n"
        for key, value in melhor_correspondencia.items():
            if isinstance(value, list):
                resposta_formatada += f"**{key}**: " + ", ".join(value) + "\n"
            else:
                resposta_formatada += f"**{key}**: {value}\n"
        return resposta_formatada

    return melhor_correspondencia if isinstance(melhor_correspondencia, str) else None



def gerar_resposta_openai(user_message, contexto=None, contexto_adicional=None):
    messages = [
        {
            "role": "system",
            "content": "Você é a IA Manuela, especialista em manutenção industrial e ativos da QuickEAM. Responda com base no contexto fornecido, sem inventar informações e sem citar diretamente documentos internos."
        }
    ]

    if contexto_adicional:
        messages.append({
            "role": "system",
            "content": f"📚 Contexto adicional:\n{contexto_adicional[:2000]}"
        })

    if contexto:
        for item in contexto:
            messages.append({"role": "user", "content": item["question"]})
            messages.append({"role": "assistant", "content": item["answer"]})

    messages.append({"role": "user", "content": user_message})

    logger.info(f"[DEBUG] Enviando para OpenAI: {json.dumps(messages, ensure_ascii=False, indent=2)}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Erro na API OpenAI: {e}")
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