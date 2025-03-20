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
    Pesquisa no JSON e retorna uma resposta formatada corretamente, evitando retorno de listas ou dicionários brutos.
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

    # ✅ Se a resposta for uma lista, formatamos de maneira mais natural
    if isinstance(melhor_correspondencia, list):
        return f"Aqui estão as informações encontradas:\n\n" + "\n".join(f"- {item}" for item in melhor_correspondencia)

    # ✅ Se a resposta for um dicionário, formatamos corretamente
    if isinstance(melhor_correspondencia, dict):
        resposta_formatada = "Aqui estão os detalhes:\n\n"
        for key, value in melhor_correspondencia.items():
            if isinstance(value, list):  # Se o valor for uma lista, formatamos adequadamente
                resposta_formatada += f"**{key.capitalize()}**:\n" + "\n".join(f"- {item}" for item in value) + "\n\n"
            else:
                resposta_formatada += f"**{key.capitalize()}**: {value}\n\n"
        return resposta_formatada.strip()  # Remove espaços extras no final

    # ✅ Se a resposta for apenas um texto simples, retorna normalmente
    if isinstance(melhor_correspondencia, str):
        return melhor_correspondencia

    return None  # Se não encontrar nada, retorna None para seguir para a OpenAI.




def gerar_resposta_openai(user_message, contexto=None, contexto_adicional=None):
    """
    Gera resposta utilizando OpenAI, considerando conhecimento da QuickEAM e arquivos enviados.
    """

    conhecimento = carregar_conhecimento()
    resposta_json = buscar_no_json(user_message, conhecimento)

    if resposta_json:
        return str(resposta_json)  # ✅ Converte para string formatada antes de retornar

    messages = [
        {"role": "system", "content": "Você é a IA Manuela, um assistente virtual especializado na empresa QuickEAM, capaz de interpretar documentos enviados e responder perguntas sobre seu conteúdo."}
    ]

    # 🔥 Adicionamos a base de conhecimento ANTES das mensagens do usuário
    base_conhecimento_contexto = json.dumps(conhecimento, ensure_ascii=False, indent=2)
    messages.append({"role": "system", "content": f"Aqui está a base de conhecimento da QuickEAM:\n{base_conhecimento_contexto}"})

    # 🔥 Se houver um arquivo PDF, ele deve ser tratado como um documento essencial para a resposta
    if contexto_adicional:
        messages.append({
            "role": "system",
            "content": f"⚠️ **IMPORTANTE**: O usuário enviou um documento relevante para análise. Abaixo está o conteúdo extraído:\n\n"
                       f"📄 **Conteúdo do Documento**:\n"
                       f"--- INÍCIO ---\n"
                       f"{contexto_adicional[:2000]}..."  # Limitamos para evitar excesso de texto
        })

    # 🔥 Se houver histórico de conversa, adicionamos para manter o contexto
    if contexto:
        for item in contexto:
            messages.append({"role": "user", "content": item["question"]})
            messages.append({"role": "assistant", "content": item["answer"]})

    # 🔥 Pergunta do usuário no final, para que a IA sempre tenha o documento antes de responder
    messages.append({"role": "user", "content": user_message})

    # 🔥 Log para debug: verificar o que está sendo enviado para a IA
    logger.info(f"[DEBUG] Enviando para OpenAI: {json.dumps(messages, ensure_ascii=False, indent=2)}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=700
        )
        resposta_ia = response.choices[0].message.content.strip()

        return resposta_ia or "Desculpe, não consegui processar sua mensagem. Tente reformular."

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
