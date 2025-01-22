from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
import re


def formatar_texto_para_html(texto):
    """Converte marcações de texto em HTML."""
    # Negrito: **texto**
    texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)
    # Itálico: *texto*
    texto = re.sub(r'\*(.*?)\*', r'<i>\1</i>', texto)
    # Sublinhado: _texto_
    texto = re.sub(r'_(.*?)_', r'<u>\1</u>', texto)
    # Títulos: ### Título
    texto = re.sub(r'(?m)^### (.*?)$', r'<h3>\1</h3>', texto)
    texto = re.sub(r'(?m)^#### (.*?)$', r'<h4>\1</h4>', texto)
    # Listas ordenadas: 1. item
    texto = re.sub(r'(?m)^\d+\.\s(.*?)$', r'<li>\1</li>', texto)
    texto = re.sub(r'(<li>.*?</li>)', r'<ol>\1</ol>', texto, flags=re.DOTALL)
    # Linha horizontal: ---
    texto = texto.replace('---', '<hr>')
    return texto


def processar_comunicacao_multi_ia(user_message, historico_completo):
    respostas = {}

    try:
        respostas['openai'] = gerar_resposta_openai(user_message, historico_completo)
    except Exception as e:
        respostas['openai'] = f"Erro na OpenAI: {e}"

    try:
        respostas['gemini'] = gemini_gerar_resposta(user_message, historico_completo)
    except Exception as e:
        respostas['gemini'] = f"Erro na Gemini: {e}"

    try:
        respostas['llama'] = gerar_resposta_llama(user_message, historico_completo)
    except Exception as e:
        respostas['llama'] = f"Erro na Llama: {e}"

    melhor_resposta = respostas['openai'] or respostas['gemini'] or respostas['llama']
    return melhor_resposta



def gerar_contexto_completo(historico):
    """
    Gera um contexto completo com base no histórico da conversa.
    """
    contexto = []
    for mensagem in historico:
        if isinstance(mensagem, dict):
            # Se for um dicionário
            contexto.append({"role": "user", "content": mensagem.get("question", "")})
            contexto.append({"role": "assistant", "content": mensagem.get("answer", "")})
        else:
            # Se for um objeto do banco de dados
            contexto.append({"role": "user", "content": mensagem.question})
            contexto.append({"role": "assistant", "content": mensagem.answer})
    return contexto

def gerar_resposta(provedor, mensagem, contexto=None):
    """
    Gerencia chamadas para diferentes provedores de IA e retorna a resposta de um provedor específico.
    """
    provedores_disponiveis = {
        'openai': gerar_resposta_openai,
        'llama': gerar_resposta_llama,
        'gemini': gemini_gerar_resposta,
    }

    if provedor not in provedores_disponiveis:
        raise ValueError(f"Provedor '{provedor}' não suportado.")

    try:
        resposta = provedores_disponiveis[provedor](mensagem, contexto)
        return resposta
    except Exception as e:
        print(f"Erro ao chamar o provedor '{provedor}': {e}")
        return "Erro ao processar a mensagem com a IA selecionada."