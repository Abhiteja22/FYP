import json
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from .models import Asset, Portfolio
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
def portfolio_optimize(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id, user=request.user)
    transactions = portfolio.get_transactions()
    time_period = portfolio.investment_time_period
    
    optimized_weights = optimize_portfolio(transactions, time_period)
    
    return Response({'optimized_weights': optimized_weights})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def riment_ai(request):
    portfolio = request.data.get('portfolio')
    if not portfolio:
        return Response({'error': 'Portfolio data is required.'}, status=400)
    money_invested = portfolio.get('money_invested') - portfolio.get('money_withdrawn')
    response = portfolio_details_AI(portfolio.get('current_assets_held'), 
                                    portfolio.get('total_value'), 
                                    portfolio.get('beta'), 
                                    money_invested, 
                                    portfolio.get('standard_deviation'), 
                                    portfolio.get('expected_return'), 
                                    portfolio.get('sharpe_ratio'), 
                                    portfolio.get('sector'), 
                                    portfolio.get('investment_time_period'), 
                                    portfolio.get('risk_aversion'), 
                                    portfolio.get('market_index'), 
                                    portfolio.get('market_index_long_name'))
    
    return Response({'response': response})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def suggest_portfolio(request):
    sector = request.data.get('sector')
    assets_held = request.data.get('assets_held')
    risk_aversion = request.data.get('risk_aversion')
    time_period = request.data.get('time_period')
    if sector == 'General':
        assets = Asset.objects.all()
    else:
        assets = Asset.objects.get('Sector')
    if not assets or not sector or not assets_held or not risk_aversion:
        return Response({'error': 'Data is required.'}, status=400)
    response, weights = suggest_portfolio_ai(assets, sector, assets_held, risk_aversion, time_period)
    
    return Response({'response': response, 'weights': weights})

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

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def notification(request):
    return 'Notification'
    
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
    permission_classes = [permissions.AllowAny]
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
        data['status'] = 'ACTIVE'
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        portfolio = queryset.get(pk=pk)
        transactions = portfolio.get_transactions()
        additional_details = get_portfolio_details_general(transactions, portfolio.investment_time_period, portfolio.market_index)
        serialized_asset = self.serializer_class(portfolio, context={'request': request}).data
        response_data = {**serialized_asset, **additional_details}
        # serializer = self.serializer_class(portfolio, context={'request': request})
        return Response(response_data)

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
    
class TransactionView(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Optionally filters the returned transactions by portfolio ID, if provided in the request.
        """
        queryset = Transaction.objects.all().order_by('transaction_date')
        portfolio_id = self.request.query_params.get('portfolio')
        if portfolio_id is not None:
            queryset = queryset.filter(portfolio__id=portfolio_id)
        return queryset

# class PortfolioAssetView(viewsets.ViewSet):
#     permission_classes = [permissions.AllowAny]
#     queryset = PortfolioAsset.objects.all()
#     serializer_class = PortfolioAssetSerializer

#     def list(self, request):
#         queryset = PortfolioAsset.objects.all() # Adjust later
#         serializer = self.serializer_class(queryset, many=True)
#         return Response(serializer.data)

#     def create(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=400)

#     def retrieve(self, request, pk=None):
#         portfolioAsset = self.queryset.get(pk=pk)
#         serializer = self.serializer_class(portfolioAsset)
#         return Response(serializer.data)

#     def update(self, request, pk=None):
#         portfolioAsset = self.queryset.get(pk=pk)
#         serializer = self.serializer_class(portfolioAsset, data= request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=400)

#     def partial_update(self, request, pk=None):
#         pass

#     def destroy(self, request, pk=None):
#         portfolioAsset = self.queryset.get(pk=pk)
#         portfolioAsset.delete()
#         return Response(status=204)