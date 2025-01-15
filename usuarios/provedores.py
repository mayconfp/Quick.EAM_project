from .openai_cliente import gerar_resposta_openai
from .llama_cliente import gerar_resposta_llama
from .gemini_cliente import gemini_gerar_resposta

def processar_comunicacao_multi_ia(user_message, historico_completo):
    """
    Processa a mensagem do usuário com múltiplas IAs e usa o OpenAI para consolidar a resposta.
    """
    respostas = {}

    # Chamada para o Llama API
    try:
        respostas['Llama'] = gerar_resposta_llama(user_message, historico_completo)
    except Exception as e:
        respostas['Llama'] = f"Erro ao se comunicar com a API do Llama: {e}"

    # Chamada para o Gemini API
    try:
        respostas['Gemini'] = gemini_gerar_resposta(user_message, historico_completo)
    except Exception as e:
        respostas['Gemini'] = f"Erro ao se comunicar com a IA Gemini: {e}"

    # Prepara o contexto para o OpenAI
    contexto_para_openai = gerar_contexto_completo(historico_completo)

    # Adiciona as respostas das IAs no contexto
    for provedor, resposta in respostas.items():
        contexto_para_openai.append({"role": "assistant", "content": f"{provedor} disse: {resposta}"})

    # Adiciona a mensagem atual do usuário no contexto
    contexto_para_openai.append({"role": "user", "content": user_message})

    # Chamada para o OpenAI para consolidar a resposta final
    try:
        resposta_final = gerar_resposta_openai("Com base nas respostas das outras IAs, forneça a melhor resposta.", contexto_para_openai)
        return resposta_final
    except Exception as e:
        return f"Erro ao processar a mensagem com o OpenAI: {e}"

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