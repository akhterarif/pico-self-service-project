from celery import shared_task

from apps.ai.models import ChatMessage, ChatStatus
from services.ai.ollama_client import OllamaClient
from services.ai.vector_store import VectorIndexer


@shared_task
def index_vectors_task():
    """Celery task to update Chroma vector DB from the latest DB state."""
    indexer = VectorIndexer()
    indexer.index_all()


@shared_task
def process_ai_chat(chat_id: int):
    chat = ChatMessage.objects.get(id=chat_id)
    try:
        indexer = VectorIndexer()
        docs = indexer.query_similar(chat.prompt, n_results=4)
        context_lines = [
            f"Source {idx + 1}: {item['document']} (meta={item['meta']})"
            for idx, item in enumerate(docs)
        ]
        context = "\n".join(context_lines)
        prompt = (
            "You are a cloud self-service assistant. Answer the user request using the following package and billing data extracted from the database. "
            "If the data does not explicitly answer the request, be honest about it.\n\n"
            f"{context}\n\nUser prompt: {chat.prompt}"
        )

        client = OllamaClient()
        response = client.chat(prompt)
        chat.response = response
        chat.source_docs = docs
        chat.status = ChatStatus.COMPLETED
        chat.error = ""
        chat.save(update_fields=["response", "status", "error", "source_docs", "updated_at"])
    except Exception as exc:
        chat.response = ""
        chat.status = ChatStatus.FAILED
        chat.error = str(exc)
        chat.save(update_fields=["response", "status", "error", "updated_at"])
