from django.contrib import admin
from .models import Asset, Portfolio, PortfolioAsset, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)

class AssetAdmin(admin.ModelAdmin):
    list_display = ("id", "ticker", "name", "country", "exchange", "sector", "industry", "asset_type")

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "creation_date", "user")

class PortfolioAssetAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "asset_ticker", "quantity",)  

# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(PortfolioAsset, PortfolioAssetAdmin)