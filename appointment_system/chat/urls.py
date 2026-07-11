from django.urls import path
from .views import ConversationListCreateView, MessageListCreateView, ConversationDetailView, UnreadCountView

urlpatterns = [
    path('conversations/', ConversationListCreateView.as_view(), name='chat-conversations'),
    path('conversations/<int:conv_id>/', ConversationDetailView.as_view(), name='chat-conversation'),
    path('conversations/<int:conv_id>/messages/', MessageListCreateView.as_view(), name='chat-messages'),
    path('unread-count/', UnreadCountView.as_view(), name='chat-unread'),
]
