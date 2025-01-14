from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta  # Nome corrigido

# Registro de provedores disponíveis
PROVEDORES_DISPONIVEIS = {
    'openai': gerar_resposta_openai,
    'llama': gerar_resposta_llama,
    'gemini': gemini_gerar_resposta,  # Nome corrigido
}

def gerar_resposta(provedor, mensagem):
    """
    Gerencia chamadas para provedores diferentes de IA.
    """
    # Verifica se o provedor está registrado
    if provedor not in PROVEDORES_DISPONIVEIS:
        raise ValueError(f"Provedor '{provedor}' não suportado.")

    # Chama a função correta com base no provedor
    try:
        resposta = PROVEDORES_DISPONIVEIS[provedor](mensagem)
        return resposta
    except Exception as e:
        print(f"Erro ao chamar o provedor '{provedor}': {e}")
        return "Erro ao processar a mensagem com a IA selecionada."