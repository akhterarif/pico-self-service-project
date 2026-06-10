from django.core.management.base import BaseCommand

from services.ai.vector_store import VectorIndexer


class Command(BaseCommand):
    help = 'Index DB content into Chroma vector store'

    def handle(self, *args, **options):
        indexer = VectorIndexer()
        indexer.index_all()
        self.stdout.write(self.style.SUCCESS('Indexed database into Chroma.'))
