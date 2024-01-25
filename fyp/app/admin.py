from django.contrib import admin
from .models import Asset, Portfolio, PortfolioAsset, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "risk_aversion",)

class AssetAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "country", "type", "exchange", "ipoDate", "delistingDate", "status")

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "alpha", "beta","creation_date")

class PortfolioAssetAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "asset_ticker", "quantity",)  

# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(PortfolioAsset, PortfolioAssetAdmin)