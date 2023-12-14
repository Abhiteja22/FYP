from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('register/', views.register, name='register'),
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolio/create/', views.portfolio_create, name='portfolio_create'),
    path('portfolio/<int:pk>/update/', views.portfolio_update, name='portfolio_update'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('assets/', views.asset_list, name='asset_list'),
    path('app/', views.app, name='app'),
    path('stocks/', views.stocks, name='stocks'),
    path('stocks/details/<int:id>', views.details, name='details')
]