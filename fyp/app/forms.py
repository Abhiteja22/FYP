from django import forms
from .models import Asset, Portfolio
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'type', 'allocation']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']

# Create a formset for assets within a portfolio
AssetFormSet = inlineformset_factory(Portfolio, Asset, form=AssetForm, extra=1)
