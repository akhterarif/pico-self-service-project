from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import AIChatSerializer
from services.ai.ollama_client import OllamaClient
from services.ai.vector_store import VectorIndexer


class AIQueryView(APIView):
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response({"error": "`text` is required"}, status=status.HTTP_400_BAD_REQUEST)
        idx = VectorIndexer()
        res = idx.query(text)
        return Response(res)


class AIChatView(APIView):
    """Simple proxy endpoint to an Ollama model for chat/explanations."""

    def post(self, request):
        serializer = AIChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prompt = serializer.validated_data["prompt"]
        client = OllamaClient()
        try:
            resp = client.chat(prompt)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"response": resp})
