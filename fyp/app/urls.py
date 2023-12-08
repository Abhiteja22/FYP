from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('register/', views.register, name='register'),
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolio/new/', views.portfolio_create, name='portfolio_new'),
    path('portfolio/<int:pk>/edit/', views.portfolio_update, name='portfolio_edit'),
    path('app/', views.app, name='app'),
    path('stocks/', views.stocks, name='stocks'),
    path('stocks/details/<int:id>', views.details, name='details')
]