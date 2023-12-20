from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# This is for testing
class Stock(models.Model):
    stockName = models.CharField(max_length=255)
    stockTicker = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.stockName} {self.stockTicker}"
    
# Extend the existing User model with a OneToOneField if you need to add user-specific data
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    risk_aversion = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return self.user.username
    
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # risk = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) #Adjust this value later
    alpha = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    beta = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Asset(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)  # E.g., stocks, bonds, etc.
    ticker = models.CharField(max_length=10, null=True)
    #value = models.DecimalField(max_digits=10, decimal_places=2) # Adjust this field later
    # allocation = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage of the asset in the portfolio
    alpha = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    beta = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    # portfolio = models.ForeignKey(Portfolio, related_name='assets', on_delete=models.CASCADE, null=True)
    # historical_performance = models.JSONField(null=True, blank=True)
    # JSONField can be useful to store a variety of performance data without creating a complex relational structure

    def __str__(self):
        return self.name
    
class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset_ticker = models.CharField(max_length=10, null=True)
    # asset_name = models.CharField(max_length=100)
    # asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateField(auto_now_add=True, null=True)

class PortfolioDetails:
    def __init__(self):
        self.assets_details = []  # To store details of each asset
        self.total_value = 0      # Total value of the portfolio
        self.expected_return = 0  # Expected return of the portfolio
        self.standard_deviation = 0  # Standard deviation of the portfolio
        self.sharpe_ratio = 0
        # Add other overall portfolio metrics as needed

    class AssetDetails:
        def __init__(self, symbol, quantity, price, std_dev, expected_return, beta, weight):
            self.symbol = symbol
            self.quantity = quantity
            self.price = price
            self.std_dev = std_dev
            self.expected_return = expected_return
            self.beta = beta
            self.weight = weight

# Signal to create or update Profile model whenever User model is updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()