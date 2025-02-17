from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
import re
import logging


logger = logging.getLogger(__name__)

PROVEDORES_VALIDOS = {
    'openai': gerar_resposta_openai,
    'llama': gerar_resposta_llama,
    'gemini': gemini_gerar_resposta,
}


def formatar_texto_para_html(texto):
    """Corrige a formatação de texto para HTML, incluindo listas, negrito, itálico e quebras de linha."""
    if not texto:
        return ""

    # 🔹 **Correção para negrito, itálico e sublinhado**
    texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)  # Negrito: **texto** → <b>texto</b>
    texto = re.sub(r'\*(.*?)\*', r'<i>\1</i>', texto)  # Itálico: *texto* → <i>texto</i>
    texto = re.sub(r'_(.*?)_', r'<u>\1</u>', texto)  # Sublinhado: _texto_ → <u>texto</u>

    # 🔹 **Correção para listas numeradas**
    texto = re.sub(r'(?m)^\d+\.\s(.*?)$', r'<li>\1</li>', texto)  # Transforma números em <li>
    texto = re.sub(r'(<li>.*?</li>)', r'<ol>\1</ol>', texto, flags=re.DOTALL)  # Garante <ol> externo

    # 🔹 **Correção para listas com hífen (-) ou asterisco (*)**
    texto = re.sub(r'(?m)^\s*[-*]\s(.*?)$', r'<li>\1</li>', texto)  # Transforma - ou * em <li>
    texto = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', texto, flags=re.DOTALL)  # Garante <ul> externo

    # 🔹 **Correção para quebras de linha**
    texto = texto.replace("\n", "<br>")

    return texto




def processar_comunicacao_multi_ia(user_message, historico):
    """Processa a mensagem consultando JSON antes de usar IAs externas."""

    # 🔎 Verifica primeiro no JSON
    resposta_json = gerar_resposta_openai (user_message)
    if resposta_json:
        return resposta_json  # Retorna a resposta se encontrada no JSON

    print(f"[DEBUG] Nenhuma resposta no JSON. Chamando IA para responder: '{user_message}'")

    # ✅ **Corrigindo o erro: inicializando 'contexto' antes de ser usado**
    contexto = historico if historico else []  
    respostas = {}

    try:
        respostas['openai'] = gerar_resposta_openai(user_message, contexto)
    except Exception as e:
        print(f"[ERROR] Erro na OpenAI: {e}")
        respostas['openai'] = None

    if not respostas.get('openai'):
        try:
            respostas['gemini'] = gemini_gerar_resposta(user_message, contexto)
        except Exception as e:
            print(f"[ERROR] Erro na Gemini: {e}")
            respostas['gemini'] = None

    if not respostas.get('openai') and not respostas.get('gemini'):
        try:
            respostas['llama'] = gerar_resposta_llama(user_message, contexto)
        except Exception as e:
            print(f"[ERROR] Erro na Llama: {e}")
            respostas['llama'] = None

    melhor_resposta = respostas.get('openai') or respostas.get('gemini') or respostas.get('llama')

    return melhor_resposta or "Desculpe, não consegui gerar uma resposta no momento."





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




def gerar_resposta(provedor, mensagem, contexto=None):
    """
    Gerencia chamadas para diferentes provedores de IA e retorna a resposta de um provedor específico.
    """

    if provedor not in PROVEDORES_VALIDOS:
        return "Erro: Provedor não suportado."

    try:
        resposta = PROVEDORES_VALIDOS[provedor](mensagem, contexto)
        return resposta
    except Exception as e:
        print(f"[ERROR] Erro ao chamar o provedor '{provedor}': {e}")
        return "Erro ao processar a mensagem com a IA selecionada."
