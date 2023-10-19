from django.contrib import admin
from .models import Stock

# For Formatting how data is displayed
class StockAdmin(admin.ModelAdmin):
    list_display = ("stockName", "stockTicker",)

# Register your models here.
admin.site.register(Stock, StockAdmin)