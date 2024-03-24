from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = DefaultRouter()
router.register('assets', views.AssetView, basename='assets')
router.register('portfolio', views.PortfolioView, basename='portfolio')
router.register('transaction', views.TransactionView, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('', views.getRoutes),
    path('optimize/<int:portfolio_id>/', views.portfolio_optimize, name='portfolio-optimize'),
    path('rimentai/', views.riment_ai, name='riment-ai'),
    path('suggest/', views.suggest_portfolio, name='suggest-portfolio'),
    path('notification/', views.notification, name='notification'),
]

# urlpatterns = [
#     path('index/', views.index, name='index'),
#     path('', views.main, name='main'),
#     path('register/', views.register, name='register'),
#     path('portfolios/', views.portfolio_list, name='portfolio_list'),
#     path('portfolio/create/', views.portfolio_create, name='portfolio_create'),
#     path('portfolio/<int:pk>/update/', views.portfolio_update, name='portfolio_update'),
#     path('portfolio/<int:pk>/details/', views.portfolio_details, name='portfolio_details'),
#     path('profile/', views.profile_view, name='profile_view'),
#     path('profile/update/', views.profile_update, name='profile_update'),
#     path('portfolio/<int:portfolio_id>/suggest_weightage/', views.portfolio_suggest_weightage, name='portfolio_suggest_weightage'),
#     path('stocks/', views.asset_list, name='asset_list'),  # Default to USA
#     path('stocks/<str:country>/', views.asset_list, name='asset_list_country'),
#     path('assets/<str:symbol>/', views.asset_detail_view, name='asset_detail'),
#     path('asset/<str:symbol>/dashboard', views.show_chart, name='asset_dashboard'),
#     path('search_stocks/', views.search_stocks, name='search_stocks'),
# ]