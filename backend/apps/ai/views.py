from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatMessage, ChatStatus
from .serializers import ChatMessageCreateSerializer, ChatMessageSerializer
from .tasks import process_ai_chat
from apps.common import is_admin
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
    """Create a chat request and schedule async processing."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prompt = serializer.validated_data["prompt"]

        chat = ChatMessage.objects.create(
            user=request.user,
            customer=getattr(request.user, "customer", None),
            prompt=prompt,
            status=ChatStatus.PENDING,
        )
        process_ai_chat.delay(chat.id)
        return Response(ChatMessageSerializer(chat).data, status=status.HTTP_201_CREATED)


class ChatListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ChatMessage.objects.select_related("user", "customer")
        if is_admin(self.request.user):
            return qs
        return qs.filter(user=self.request.user)


class ChatDetailView(generics.RetrieveAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ChatMessage.objects.select_related("user", "customer")
        if is_admin(self.request.user):
            return qs
        return qs.filter(user=self.request.user)
