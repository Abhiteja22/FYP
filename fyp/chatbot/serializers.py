from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import *
from .utils import chatbot

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ("id", "name")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop(password)
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        Token.objects.create(user=user)
        return user
    
class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(request=self.context.get("request"), username=username, password=password)
        if not user:
            msg = "Credentials are not provided correctly"
            raise serializers.ValidationError(msg, code="authentication")
        attrs["user"] = user
        return attrs
    
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "input", "output", "chat")
        extra_kwargs = {
            "output": {"read_only": True}
        }