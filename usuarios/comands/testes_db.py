from django.core.management.base import BaseCommand
from usuarios.models import ChatHistory

class Command(BaseCommand):
    help = "Testa a conexão com o banco de dados"

    def handle(self, *args, **kwargs):
        try:
            ChatHistory.objects.create(
                question="Teste conexão DB",
                answer="Conexão bem-sucedida",
                user=None
            )
            self.stdout.write(self.style.SUCCESS("Registro salvo com sucesso no banco de dados."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao conectar e salvar no banco: {e}"))
