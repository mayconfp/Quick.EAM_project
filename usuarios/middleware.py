# usuarios/middleware.py
import requests
from django.utils.translation import activate

def get_ip(request):
    """
    Obtém o endereço IP do usuário.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class LocalizacaoMiddleware:
    """
    Middleware para definir o idioma do usuário com base na localização.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            ip_usuario = get_ip(request)
            url = f"http://api.ipstack.com/{ip_usuario}?access_key=YOUR_ACCESS_KEY"
            response = requests.get(url)
            dados_localizacao = response.json()
            pais = dados_localizacao.get('country_code', 'EN')

            mapa_idiomas = {
                'BR': 'pt-br',
                'US': 'en',
                'ES': 'es',
            }

            idioma = mapa_idiomas.get(pais, 'en')
            activate(idioma)
            request.session['django_language'] = idioma
        except Exception as e:
            print(f"Erro ao determinar idioma: {e}")
            activate('en')  # Idioma padrão

        response = self.get_response(request)
        return response