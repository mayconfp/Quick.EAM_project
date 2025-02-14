from .openai_cliente import gerar_resposta_openai, carregar_conhecimento, buscar_resposta_no_json
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

def gerar_contexto_completo(historico):
    """
    Gera um contexto completo com base no histórico da conversa.
    """
    contexto = []
    for mensagem in historico:
        if isinstance(mensagem, dict):
            contexto.append({"role": "user", "content": mensagem.get("question", "")})
            contexto.append({"role": "assistant", "content": mensagem.get("answer", "")})
        else:
            contexto.append({"role": "user", "content": mensagem.question})
            contexto.append({"role": "assistant", "content": mensagem.answer})
    return contexto

def processar_comunicacao_multi_ia(user_message, historico):
    """Processa a mensagem do usuário consultando primeiro o JSON, depois contexto, e por último as IAs externas."""

    conhecimento = carregar_conhecimento()

    # 🚀 **PASSO 1: Verifica no JSON**
    resposta_json = buscar_resposta_no_json(user_message)

    if resposta_json:
        return resposta_json  # Se encontrado no JSON, retorna a resposta direto

    # 🚀 **PASSO 2: Gera contexto baseado no histórico da conversa**
    contexto = gerar_contexto_completo(historico)

    # 🚀 **PASSO 3: Se não estiver no JSON, consulta as IAs externas**
    respostas = {}

    try:
        respostas['openai'] = gerar_resposta_openai(user_message, contexto)
    except Exception as e:
        respostas['openai'] = f"Erro na OpenAI: {e}"

    try:
        respostas['gemini'] = gemini_gerar_resposta(user_message, contexto)
    except Exception as e:
        respostas['gemini'] = f"Erro na Gemini: {e}"

    try:
        respostas['llama'] = gerar_resposta_llama(user_message, contexto)
    except Exception as e:
        respostas['llama'] = f"Erro na Llama: {e}"

    melhor_resposta = respostas.get('openai') or respostas.get('gemini') or respostas.get('llama')

    return melhor_resposta or "Desculpe, não consegui gerar uma resposta para essa pergunta."

def gerar_resposta(provedor, mensagem, contexto=None):
    """
    Gerencia chamadass para diferentes provedores de IA e retorna a resposta de um provedor específico.
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
