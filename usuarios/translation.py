from modeltranslation.translator import register, TranslationOptions  # ✅ Correto!
from .models import Categoria  # Certifique-se de importar seus modelos corretamente

@register(Categoria)
class CategoriaTranslationOptions(TranslationOptions):
    fields = ('descricao',)  # Lista dos campos que serão traduzidos
