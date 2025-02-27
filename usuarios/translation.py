from modeltranslation.translator import register, TranslationOptions
from .models import CategoriaLang

@register(CategoriaLang)
class CategoriaLangTranslationOptions(TranslationOptions):
    fields = ('descricao',)