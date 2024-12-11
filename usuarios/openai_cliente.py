import openai
import os
from usuarios.models import ChatHistory

openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_resposta(mensagem_usuario, user=None):
    """
    Gera uma resposta da OpenAI e salva a interação no banco de dados.
    """
    try:
        # Chamada para a API da OpenAI
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mensagem_usuario}]
        )
        conteudo_resposta = resposta['choices'][0]['message']['content']
        print(f"Resposta da OpenAI: {conteudo_resposta}")

        # Salvar no banco de dados se o usuário estiver autenticado
        if user:
            ChatHistory.objects.create(
                user=user,
                question=mensagem_usuario,
                answer=conteudo_resposta
            )
            print(f"Histórico salvo: Pergunta='{mensagem_usuario}', Resposta='{conteudo_resposta}'")

        return conteudo_resposta
    except Exception as e:
        print(f"Erro ao se comunicar com a OpenAI: {e}")
        return "Houve um erro ao gerar a resposta. Tente novamente mais tarde."
