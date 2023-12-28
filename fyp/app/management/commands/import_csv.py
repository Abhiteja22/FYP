import csv
from django.core.management.base import BaseCommand
from app.models import Asset
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Load a CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('app/static/stock_csv_files/list_of_usstocks_alpha_vantage.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                ipoDate = parse_date(row[4]) if row[4] != 'null' else None
                delistingDate = parse_date(row[5]) if row[5] != 'null' else None

                _, created = Asset.objects.get_or_create(
                    ticker=row[0],
                    name=row[1],
                    exchange=row[2],
                    type=row[3],
                    ipoDate=ipoDate,
                    delistingDate=delistingDate,
                    status=row[6]
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Asset added: {row[1]}'))
