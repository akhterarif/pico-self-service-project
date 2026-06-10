from celery import shared_task

from services.ai.vector_store import VectorIndexer


@shared_task
def index_vectors_task():
    """Celery task to update Chroma vector DB from the latest DB state."""
    indexer = VectorIndexer()
    indexer.index_all()
