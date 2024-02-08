from django.urls import path
from . import views

urlpatterns = [
     path("", views.home, name="chatbot_home"),
     path("chatbot/", views.chatbot, name="chatbot"),
     path("chat/", views.ChatView.as_view(), name="chat"),
     path("chat/<int:pk>/", views.SingleChatView.as_view(), name="chat"),
     path("users/", views.UserView.as_view(), name="users"),
     path("tokens/", views.TokenView.as_view(), name="tokens"),
     path('chat/messages/<int:pk>/', views.MessageView.as_view(), name='chat_messages'),
     path('chat/delete/<int:pk>/', views.ChatView.as_view(), name='delete_chat'),
]
