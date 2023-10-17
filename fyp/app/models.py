from django.db import models

# Create your models here.

class Stock(models.Model):
    stockName = models.CharField(max_length=255)
    stockTicker = models.CharField(max_length=10)
