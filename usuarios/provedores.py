from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
import logging
import re

logger = logging.getLogger(__name__)

PROVEDORES_VALIDOS = {
    'openai': gerar_resposta_openai,
    'llama': gerar_resposta_llama,
    'gemini': gemini_gerar_resposta,
}




def formatar_texto_para_html(texto):
    """Converte formatações de texto para HTML corretamente."""

    if not texto:
        return ""

    # ✅ **Garante que o texto seja uma string**
    if isinstance(texto, list):
        texto = " ".join(map(str, texto))

    # ✅ **Negrito:** **Texto** → <b>Texto</b>
    texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)

    # ✅ **Itálico:** *Texto* → <i>Texto</i>
    texto = re.sub(r'\*(?!\*)(.*?)\*', r'<i>\1</i>', texto)

    # ✅ **Sublinhado:** _Texto_ → <u>Texto</u>
    texto = re.sub(r'_(.*?)_', r'<u>\1</u>', texto)

    # ✅ **Cabeçalhos:** ### Título → <h3>Título</h3>
    texto = re.sub(r'(?m)^### (.*?)$', r'<h3>\1</h3>', texto)
    texto = re.sub(r'(?m)^#### (.*?)$', r'<h4>\1</h4>', texto)

    # ✅ **Listas Ordenadas:** 1. item → <ol><li>item</li></ol>
    texto = re.sub(r'(?m)^\d+\.\s+(.*?)$', r'<li>\1</li>', texto)
    if "<li>" in texto:
        texto = "<ol>" + texto + "</ol>"

    # ✅ **Listas Não Ordenadas:** - item → <ul><li>item</li></ul>
    texto = re.sub(r'(?m)^\s*[-*]\s+(.*?)$', r'<li>\1</li>', texto)
    if "<li>" in texto:
        texto = "<ul>" + texto + "</ul>"

    # ✅ **Substituir quebras de linha por `<br>`**
    texto = texto.replace("\n", "<br>")

    return texto




def processar_comunicacao_multi_ia(user_message, historico):
    """Garante que a IA responda a todas as partes da pergunta."""

    if not user_message.strip():
        return "A mensagem não pode estar vazia."

    respostas = {}

    try:
        resposta_openai = gerar_resposta_openai(user_message, historico)
        if isinstance(resposta_openai, list):
            resposta_openai = " ".join(resposta_openai)  # Junta listas em um texto contínuo
        respostas['openai'] = resposta_openai
    except Exception as e:
        print(f"[ERROR] Erro na OpenAI: {e}")
        respostas['openai'] = None

    if not respostas['openai']:
        try:
            resposta_gemini = gemini_gerar_resposta(user_message, historico)
            if isinstance(resposta_gemini, list):
                resposta_gemini = " ".join(resposta_gemini)
            respostas['gemini'] = resposta_gemini
        except Exception as e:
            print(f"[ERROR] Erro na Gemini: {e}")
            respostas['gemini'] = None

    if not respostas['openai'] and not respostas['gemini']:
        try:
            resposta_llama = gerar_resposta_llama(user_message, historico)
            if isinstance(resposta_llama, list):
                resposta_llama = " ".join(resposta_llama)
            respostas['llama'] = resposta_llama
        except Exception as e:
            print(f"[ERROR] Erro na Llama: {e}")
            respostas['llama'] = None

    melhor_resposta = respostas.get('openai') or respostas.get('gemini') or respostas.get('llama')

    if melhor_resposta:
        # **Correção: Dividir e validar se todas as partes foram respondidas**
        if "e quem está desenvolvendo" in user_message.lower():
            if "Maycon" not in melhor_resposta and "Júlio" not in melhor_resposta:
                melhor_resposta += "\nOs responsáveis pelo desenvolvimento são: Maycon Felipe, Júlio Cesar e Tatiana Santos."

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
