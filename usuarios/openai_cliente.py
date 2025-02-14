import json
import os
import openai
from dotenv import load_dotenv, find_dotenv

# 🔑 Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")


def carregar_conhecimento():
    """Carrega o JSON de conhecimento."""
    caminho_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "../knowledge.json"))
    try:
        with open(caminho_json, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def buscar_resposta_no_json(pergunta):
    """
    Busca uma resposta no JSON com base na pergunta feita pelo usuário.
    """
    conhecimento = carregar_conhecimento()
    pergunta = pergunta.lower().strip()

    if "quem desenvolveu" in pergunta or "quem fez o projeto" in pergunta or "quem participou" in pergunta:
        equipe = conhecimento.get("equipe", {})
        devs = ", ".join(equipe.get("desenvolvedores", []))
        supervisor = equipe.get("supervisor", {})
        feedback = equipe.get("usuaria_feedback", {}).get("nome", "Desconhecido")
        return f"O projeto foi desenvolvido por {devs}, com supervisão de {supervisor}. A usuária {feedback} ajudou fornecendo feedbacks essenciais."

    if "zander" in pergunta:
        return f"Zander Reis foi o Supervisor do projeto QuickEAM."

    if "tatiana" in pergunta:
        return f"Tatiana foi uma pessoa muito importante para o projeto. Ela testou o sistema e forneceu feedbacks essenciais."

    if "tecnologias" in pergunta or "ferramentas" in pergunta:
        tecnologias = conhecimento.get("tecnologias_utilizadas", {})
        return "\n".join([f"{k}: {', '.join(v)}" for k, v in tecnologias.items()])

    if "como foi feito o projeto" in pergunta:
        return "\n".join(conhecimento.get("historico_projeto", []))

    return None  # Retorna None caso a pergunta não seja encontrada no JSON


def buscar_no_contexto(pergunta, contexto):
    """
    Verifica se a pergunta já foi respondida antes no contexto.
    """
    for item in contexto:
        if pergunta in item['question'].lower():
            return item['answer']
    return None


def gerar_resposta_openai(user_message, contexto=None):
    if contexto is None:
        contexto = []
    elif not isinstance(contexto, list):
        print("[ERROR] O contexto não é uma lista válida")
        contexto = []

    # Garantindo que o contexto tenha estrutura correta
    contexto_formatado = []
    for item in contexto:
        if isinstance(item, dict) and "question" in item and "answer" in item:
            contexto_formatado.append({"role": "user", "content": item["question"]})
            contexto_formatado.append({"role": "assistant", "content": item["answer"]})

    # Adiciona contexto formatado à requisição da OpenAI
    messages = [
        {"role": "system",
         "content": f"Você é {carregar_conhecimento().get('nome_assistente', 'um assistente virtual')}."},
        {"role": "user", "content": user_message}
    ] + contexto_formatado
