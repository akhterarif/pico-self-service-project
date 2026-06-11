from rest_framework import serializers

from .models import ChatMessage


class AIChatSerializer(serializers.Serializer):
    prompt = serializers.CharField()


class ChatMessageCreateSerializer(serializers.Serializer):
    prompt = serializers.CharField()


class ChatMessageSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    customer_name = serializers.CharField(source="customer.company_name", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "user_email",
            "customer_name",
            "prompt",
            "response",
            "status",
            "error",
            "source_docs",
            "created_at",
            "updated_at",
        ]
