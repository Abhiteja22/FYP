import json
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from .models import Asset, PortfolioAsset, Portfolio
from .utils import *

def get_user_by_username(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None

def get_portfolios(username):
    """
    Retrieves user's list of portfolios

    :param username: The username to whom the portfolio belongs.
    """
    user = get_user_by_username(username)
    portfolio = Portfolio.objects.filter(user=user)

    return portfolio

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/test/'
    ]
    return Response(routes)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def getAssetsEndPoint(request):
    if request.method == 'GET':
        assets = Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response("Invalid request method", status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulation {request.user}, your API just responded to GET request"
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            if 'text' not in data:
                return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
            text = data.get('text')
            data = f'Congratulation your API just responded to POST request with text: {text}'
            return Response({'response': data}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
    return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
    
# class based view to register user
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
        
class AssetView(viewsets.ViewSet):
    queryset = Asset.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssetSerializer

    def list(self, request):
        queryset = Asset.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        asset = self.queryset.get(pk=pk)
        additional_details = get_asset_details_general(asset.ticker)
        serialized_asset = self.serializer_class(asset).data
        response_data = {**serialized_asset, **additional_details}
        return Response(response_data)
    
class PortfolioView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        """
        This view should return a list of all the portfolios
        for the currently authenticated user.
        """
        user = self.request.user
        return Portfolio.objects.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data.copy()
        data['user'] = request.user.pk
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        portfolio = queryset.get(pk=pk)
        serializer = self.serializer_class(portfolio, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        portfolio = queryset.get(pk=pk)
        data = request.data.copy()
        data['user'] = request.user.pk
        serializer = self.serializer_class(portfolio, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        portfolio = queryset.get(pk=pk)
        portfolio.delete()
        return Response(status=204)
    
class PortfolioAssetView(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = PortfolioAsset.objects.all()
    serializer_class = PortfolioAssetSerializer

    def list(self, request):
        queryset = PortfolioAsset.objects.all() # Adjust later
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        portfolioAsset = self.queryset.get(pk=pk)
        serializer = self.serializer_class(portfolioAsset)
        return Response(serializer.data)

    def update(self, request, pk=None):
        portfolioAsset = self.queryset.get(pk=pk)
        serializer = self.serializer_class(portfolioAsset, data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        portfolioAsset = self.queryset.get(pk=pk)
        portfolioAsset.delete()
        return Response(status=204)