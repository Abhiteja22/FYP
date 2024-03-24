import csv
from django.core.management.base import BaseCommand
from app.models import Asset
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Load a CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('app/static/us_symbols.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                # Since the CSV now only includes ticker, name, and exchange, 
                # we simplify the object creation accordingly.
                _, created = Asset.objects.get_or_create(
                    ticker=row[0],  # Ticker symbol
                    name=row[1],    # Name of the asset
                    exchange=row[2] # Exchange where the asset is listed
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Asset added: {row[1]}'))
        # Update assets with additional info from the second CSV
        with open('app/static/nasdaq_screener_1710093974408.csv', 'r') as file:
            reader = csv.DictReader(file)  # Using DictReader for easy access by column header
            for row in reader:
                try:
                    asset = Asset.objects.get(ticker=row['Symbol'])
                    asset.country = row['Country'] if row['Country'] else None
                    asset.ipoYear = int(row['IPO Year']) if row['IPO Year'] else None  # Assuming IPO Year is an integer
                    if row['Sector'] == 'Health Care':
                        asset.sector = 'Healthcare'
                    else:
                        asset.sector = row['Sector'] if row['Sector'] else None
                    asset.industry = row['Industry'] if row['Industry'] else None
                    asset.save()
                    self.stdout.write(self.style.SUCCESS(f'Asset updated: {asset.name}'))
                except Asset.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Asset not found for ticker: {row["Symbol"]}'))
