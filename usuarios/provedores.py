from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta
import markdown
from django.utils.safestring import mark_safe


PROVEDORES_VALIDOS = {
    'openai': gerar_resposta_openai,
    'llama': gerar_resposta_llama,
    'gemini': gemini_gerar_resposta,
}

def formatar_texto_para_html(texto):
    """Converte marcações de texto em HTML e melhora a formatação da tabela."""
    if not texto:
        return ""

    # 🔹 Adiciona um CSS para melhorar a aparência da tabela
    estilo_tabela = """
    <style>
            table {
            border-collapse: collapse;
            width: 100%;
            max-width: 100%;
            overflow-x: auto;
            display: block;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
            font-size: 14px;
        }
        th {
            background-color: #4CAF50;
            color: white;
            text-align: center;
        }
        td {
            background-color: #f9f9f9;
        }
        ul, ol {
            margin-left: 20px;
        }
    </style>
    """

    # 🔹 Converter Markdown para HTML (com suporte a tabelas e listas)
    texto = markdown.markdown(texto, extensions=['extra', 'tables'])

    # 🔹 Adiciona o estilo no início do texto
    texto = estilo_tabela + texto

    return mark_safe(texto)

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