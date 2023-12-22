from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('register/', views.register, name='register'),
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolio/create/', views.portfolio_create, name='portfolio_create'),
    path('portfolio/<int:pk>/update/', views.portfolio_update, name='portfolio_update'),
    path('portfolio/<int:pk>/details/', views.portfolio_details, name='portfolio_details'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('portfolio/<int:portfolio_id>/suggest_weightage/', views.portfolio_suggest_weightage, name='portfolio_suggest_weightage'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/<str:symbol>/', views.asset_detail_view, name='asset_detail'),
    path('search_stocks/', views.search_stocks, name='search_stocks'),
]