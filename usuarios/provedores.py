from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from gemini_cliente import gemini_gerar_respota

# Registro de provedores disponíveis
PROVEDORES_DISPONIVEIS = {
    'openai': gerar_resposta_openai,
    'llama': gerar_resposta_llama,
    'gemini': gemini_gerar_respota,
}

def gerar_resposta(provedor, mensagem):
    """
    Gerencia chamadas para provedores diferentes de IA.
    """

    # Verifica se o provedor está registrado
    if provedor not in PROVEDORES_DISPONIVEIS:
        raise ValueError(f"Provedor '{provedor}' não suportado.")

    # Chama a função correta com base no provedor
    resposta = PROVEDORES_DISPONIVEIS[provedor](mensagem)

    print(f"[DEBUG] Resposta gerada pelo provedor '{provedor}': {resposta}")
    return resposta
