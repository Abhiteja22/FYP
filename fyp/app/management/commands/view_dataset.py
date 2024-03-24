from django.core.management.base import BaseCommand
from app.models import Asset
import yfinance as yf

class Command(BaseCommand):
    help = 'Finds all assets with no country specified'

    def handle(self, *args, **kwargs):
        # Filter assets with the old sector value and update them
        assets = Asset.objects.all()
        currencies = set()
        
        for asset in assets:
            info = yf.Ticker(asset.ticker)
            currency = 'NA'
            try:
                currency = info.info.get('currency')
                
                currencies.add(currency)
            except:
                self.stdout.write(self.style.ERROR(f'{asset.ticker} no currency'))
            # Save the country as the asset country
            self.stdout.write(self.style.SUCCESS(f'{asset.name} ({asset.ticker}) currency is {currency}'))
        
        self.stdout.write(self.style.WARNING(f'These are the currencies: {len(currencies)} currencies'))
        for currency in currencies:
            self.stdout.write(self.style.WARNING(f'{currency}'))