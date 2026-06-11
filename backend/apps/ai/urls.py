from django.urls import path

from .views import AIChatView, AIQueryView, ChatListView, ChatDetailView

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai-chat'),
    path('chats/', ChatListView.as_view(), name='ai-chat-list'),
    path('chats/<int:pk>/', ChatDetailView.as_view(), name='ai-chat-detail'),
    path('query/', AIQueryView.as_view(), name='ai-query'),
]
