import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from django.utils.translation import gettext_lazy as _
import os
from dotenv import load_dotenv, find_dotenv
from django.utils.translation import gettext_lazy as gettext


load_dotenv(find_dotenv())

LANGUAGES = [
    ('en', gettext('English')),
    ('pt-br', gettext('Portuguese')),
]


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta")

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',  # Aplicativo da sua aplicação
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Middleware de autenticação
    'django.contrib.messages.middleware.MessageMiddleware',  # Middleware de mensagens
    'usuarios.middleware.LocalizacaoMiddleware',  # Seu middleware customizado
]




ROOT_URLCONF = 'DjangoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'testes',
        'USER': 'postgres',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'usuarios.validators.SenhaPersonalizada'},
]

AUTH_USER_MODEL = 'usuarios.CustomUser'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/chat/'  # Redireciona para a página de chat após o login


# Configurações de Internacionalização (i18n)
LANGUAGE_CODE = 'pt-br'


LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configurações estáticas
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "usuarios", "static"),]

# Chaves de API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
RECEITA_API_URL = os.getenv("RECEITA_API_URL", "https://receitaws.com.br/v1/cnpj/")


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

#

AUTHENTICATION_BACKENDS = [
    'usuarios.authentication_backends.UsernameOrCNPJBackend',  # Caminho correto para o backend
    'django.contrib.auth.backends.ModelBackend',
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')