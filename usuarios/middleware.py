import requests
from django.utils.translation import activate
from django.utils.deprecation import MiddlewareMixin
import os

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '').strip()
    return ip or "127.0.0.1"

class LocalizacaoMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if "django_language" in request.session:
            activate(request.session["django_language"])
            return

        try:
            ip_usuario = get_ip(request)
            url = f"http://api.ipstack.com/{ip_usuario}?access_key={os.getenv('IPSTACK_API_KEY')}"
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            dados_localizacao = response.json()
            pais = dados_localizacao.get("country_code", "EN").upper()
            mapa_idiomas = {
                "BR": "pt-br",
                "US": "en",
                "ES": "es",
            }
            idioma = mapa_idiomas.get(pais, "en")
            activate(idioma)
            request.session["django_language"] = idioma
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"Erro ao determinar idioma: {e}")
            activate("en")