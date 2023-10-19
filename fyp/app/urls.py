from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('app/', views.app, name='app'),
    path('stocks/', views.stocks, name='stocks'),
    path('stocks/details/<int:id>', views.details, name='details')
]