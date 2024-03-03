from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
# TODO: Remove risk_free_rate and expected_market_return and adjust how data is to be shown
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    risk_aversion = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    investment_time_period = models.CharField(max_length=20, null=True)
    risk_free_rate = models.DecimalField(max_digits=7, decimal_places=5, null=True, blank=True, help_text="Annual risk-free rate of return")
    expected_market_return = models.DecimalField(max_digits=7, decimal_places=5, null=True, blank=True, help_text="Annual expected return of the market")
    market_index = models.CharField(max_length=10, null=True, help_text="Ticker symbol of the market index used for calculations")

    def __str__(self):
        return self.user.username
    def formatted_risk_free_rate(self):
        return "{:.3%}".format(self.risk_free_rate)
    def formatted_expected_market_return(self):
        return "{:.3%}".format(self.expected_market_return)
    
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    alpha = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    beta = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Asset(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    ipoDate = models.DateField(null=True)
    exchange = models.CharField(max_length=50, null=True)
    delistingDate = models.DateField(null=True)
    type = models.CharField(max_length=100, null=True)  # E.g., stocks, bonds, etc.
    STATUS_CHOICES = [('Active', 'Active'),('Delisted', 'Delisted'),]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active', null=True)
    country = models.CharField(max_length=100, default="USA")

    def __str__(self):
        return self.name
    
class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='assets')
    asset_ticker = models.CharField(max_length=10, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateField(auto_now_add=True, null=True)

# Signal to create or update Profile model whenever User model is updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()