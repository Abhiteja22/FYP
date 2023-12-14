from django.contrib import admin
from .models import Asset, Portfolio, Profile, Stock

# For Formatting how data is displayed
class StockAdmin(admin.ModelAdmin):
    list_display = ("stockName", "stockTicker",)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "risk_aversion",)

class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "alpha", "beta",)

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "alpha", "beta",)

# Register your models here.
admin.site.register(Stock, StockAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Portfolio, PortfolioAdmin)