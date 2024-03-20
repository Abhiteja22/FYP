from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import *
from .utils import get_portfolio_value, get_long_name, get_asset_price_by_date

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        # ...
        return token
    
# Serializer to register user
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = { 'first_name': {'required': True}, 'last_name': {'required': True} }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields don't match."}
            )
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    portfolio_value = serializers.SerializerMethodField()
    market_index_long_name = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = '__all__'

    def get_portfolio_value(self, obj):
        transactions = obj.get_transactions()
        assets_held = {}
        for transaction in transactions:
            asset = transaction.asset.ticker
            if transaction.transaction_type == 'BUY':
                if asset in assets_held:
                    assets_held[asset] += transaction.quantity
                else:
                    assets_held[asset] = transaction.quantity
            elif transaction.transaction_type == 'SELL':
                if asset in assets_held:
                    assets_held[asset] -= transaction.quantity
                else:
                    assets_held[asset] = transaction.quantity
        values, total_value = get_portfolio_value(assets_held)
        return total_value
    
    def get_market_index_long_name(self, obj):
        market_index = obj.market_index
        return get_long_name(market_index)
    
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'portfolio', 'asset', 'transaction_type', 'quantity', 'transaction_date']
        read_only_fields = ['value']

    def create(self, validated_data):
        asset = validated_data['asset']
        transaction_date = validated_data['transaction_date']
        quantity = validated_data['quantity']
        print(asset.ticker)
        price_per_unit = get_asset_price_by_date(asset.ticker, transaction_date)
        total_value = price_per_unit * float(quantity)
        validated_data['value'] = total_value
        transaction = Transaction.objects.create(**validated_data)
        
        return transaction

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.value = self.calculate_value(instance)
        instance.save()
        
        return instance

    def calculate_value(self, instance):
        price_per_unit = get_asset_price_by_date(instance.asset.ticker, instance.transaction_date)
        total_value = price_per_unit * float(instance.quantity)
        return total_value