from rest_framework import serializers


class AIChatSerializer(serializers.Serializer):
    prompt = serializers.CharField()
