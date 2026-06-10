from django.urls import path

from .views import AIChatView, AIQueryView

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai-chat'),
    path('query/', AIQueryView.as_view(), name='ai-query'),
]
