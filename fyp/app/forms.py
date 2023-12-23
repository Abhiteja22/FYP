from django import forms
from .models import Asset, Portfolio, Profile, PortfolioAsset
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    RISK_CHOICES = [
        (3, 'Low Risk'),
        (2.5, 'Below Average Risk'),
        (2, 'Average Risk'),
        (1.5, 'Above Average Risk'),
        (1, 'High Risk'),
    ]
    TIME_PERIOD_CHOICES = [
        ('3month', 'Short-term (3 months)'),
        ('2year', 'Short-Mid term (2 years)'),
        ('5year', 'Mid term (5 years)'),
        ('10year', 'Mid-Long term (10 years)'),
        ('30year', 'Long-term (30 years)'),
    ]
    INDEX_CHOICES = [
        ('SPY', 'S&P 500 - USA'),
        ('FTSE', 'FTSE 100 - UK'), # Does not show
        # ... other indexes ...
    ]

    risk_aversion = forms.ChoiceField(choices=RISK_CHOICES)
    investment_time_period = forms.ChoiceField(choices=TIME_PERIOD_CHOICES)
    market_index = forms.ChoiceField(choices=INDEX_CHOICES)

    class Meta:
        model = Profile
        fields = ['risk_aversion', 'investment_time_period', 'market_index']

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'type']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']

# Create a formset for assets within a portfolio
# AssetFormSet = inlineformset_factory(Portfolio, Asset, form=AssetForm, extra=1)

class AddToPortfolioForm(forms.ModelForm):
    class Meta:
        model = PortfolioAsset
        fields = ['portfolio', 'quantity']
