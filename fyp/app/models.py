from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# class CustomUser(AbstractUser):
#     email = models.EmailField(max_length=200, unique=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
    
# TODO: Remove risk_free_rate and expected_market_return and adjust how data is to be shown
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.user.username
    def formatted_risk_free_rate(self):
        return "{:.3%}".format(self.risk_free_rate)
    def formatted_expected_market_return(self):
        return "{:.3%}".format(self.expected_market_return)
    
class Portfolio(models.Model):
    INVESTMENT_PERIOD_CHOICES = [
        ('1month', '1 Month'),
        ('3month', '3 Months'),
        ('6month', '6 Months'),
        ('1year', '1 Year'),
        ('3year', '3 Years'),
        ('5year', '5 Years'),
        ('10year', '10 Years'),
        ('30year', '30 Years'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SOLD', 'Sold'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    risk_aversion = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(4)], null=True, blank=True,)
    market_index = models.CharField(max_length=10, null=True, blank=True, help_text="Ticker symbol of the market index used for calculations")
    investment_time_period = models.CharField(max_length=6, choices=INVESTMENT_PERIOD_CHOICES, null=True)
    creation_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, null=True, blank=True,)
    sell_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_portfolio_assets(self):
        return self.assets.all()
    
class Asset(models.Model):
    SECTOR_CHOICES = [
        ('Finance', 'Finance'),
        ('Healthcare', 'Healthcare'),
        ('Telecommunications', 'Telecommunications'),
        ('Basic Materials', 'Basic Materials'),
        ('Industrials', 'Industrials'),
        ('Consumer Staples', 'Consumer Staples'),
        ('Utilities', 'Utilities'),
        ('Real Estate', 'Real Estate'),
        ('Energy', 'Energy'),
        ('Consumer Discretionary', 'Consumer Discretionary'),
        ('Technology', 'Technology'),
        ('Miscellaneous', 'Miscellaneous'),
    ]

    ASSET_TYPE_CHOICES = [
        ('ETF', 'ETF'),
        ('Stock', 'Stock'),
    ]

    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    exchange = models.CharField(max_length=50, null=True, blank=True)
    ipoYear = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name
    
class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE, related_name='assets')
    asset_ticker = models.CharField(max_length=10, null=True, blank=True)
    asset_name = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateField(auto_now_add=True, null=True)
    date_sold = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.asset_ticker} in {self.portfolio.name}"

# Signal to create or update Profile model whenever User model is updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()