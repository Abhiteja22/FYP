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
    allocation = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage of the asset in the portfolio
    alpha = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    beta = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    portfolio = models.ForeignKey(Portfolio, related_name='assets', on_delete=models.CASCADE, null=True)
    # historical_performance = models.JSONField(null=True, blank=True)
    # JSONField can be useful to store a variety of performance data without creating a complex relational structure

    def __str__(self):
        return self.name

# Signal to create or update Profile model whenever User model is updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()