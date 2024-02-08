from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import views, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from .models import Chat, Message
from .serializers import *

def home(requests):
    return HttpResponse("Hello Chatbot!")

class ChatView(views.APIView):
    serializer_class = ChatSerializer
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        qs = Chat.objects.all()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        chat = Chat.objects.get(pk=pk)
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SingleChatView(views.APIView):
    serializer_class = ChatSerializer
    authentication_classes = [TokenAuthentication]

    def get(self, request, pk, format=None): 
        qs = Chat.objects.get(pk=pk)
        serializer = self.serializer_class(qs, many=False)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        chat = Chat.objects.get(pk=pk)
        serializer = ChatSerializer(chat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageView(views.APIView):
    serializer_class = MessageSerializer
    authentication_classes = [TokenAuthentication]

    def get(self, request, pk, format=None):
        qs = Message.objects.filter(chat=pk)
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, pk, format=None):
        chat = get_object_or_404(Chat, pk=pk)
        data = request.data.copy()
        data['chat'] = chat.pk
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserView(views.APIView):
    serializer_class = UserSerializer
    def get(self, request, format=None):
        qs = User.objects.all()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenView(ObtainAuthToken):
    serializer_class = TokenSerializer