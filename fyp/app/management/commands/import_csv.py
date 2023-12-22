import csv
from django.core.management.base import BaseCommand
from app.models import Asset  # Import your model

class Command(BaseCommand):
    help = 'Load a CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('app/static/stock_csv_files/london_exchange.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                _, created = Asset.objects.get_or_create(
                    ticker=row[0],
                    name=row[1],
                    country=row[2],
                    exchange=row[3],
                    currency=row[4],
                    type=row[5],
                    isin=row[6]
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Asset added: {row[1]}'))
