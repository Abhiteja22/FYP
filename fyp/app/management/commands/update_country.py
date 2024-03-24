from django.core.management.base import BaseCommand
from app.models import Asset
import yfinance as yf

class Command(BaseCommand):
    help = 'Finds all assets with no country specified'

    def handle(self, *args, **kwargs):
        # Filter assets with the old sector value and update them
        assets = Asset.objects.filter(country=None)
        countries = set()
        
        for asset in assets:
            info = yf.Ticker(asset.ticker)
            country = 'NA'
            try:
                country = info.info.get('country', 'NA')  # Safely get country info; defaults to 'NA' if not found
                asset.country = country  # Update the asset's country field
                asset.save()  # Save the changes to the database
                countries.add(country)
            except:
                self.stdout.write(self.style.ERROR(f'{asset.ticker} no country'))
            # Save the country as the asset country
            self.stdout.write(self.style.SUCCESS(f'{asset.name} ({asset.ticker}) country is {country}'))
        
        self.stdout.write(self.style.WARNING(f'These are the countries: {len(countries)} countries'))
        for country in countries:
            self.stdout.write(self.style.WARNING(f'{country}'))