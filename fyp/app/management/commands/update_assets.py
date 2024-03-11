import yfinance as yf
from django.core.management.base import BaseCommand
from app.models import Asset
import time

class Command(BaseCommand):
    help = 'Updates assets with type, sector, and industry data from Yahoo Finance'

    def handle(self, *args, **kwargs):
        assets = Asset.objects.all()
        missing_sectors = set()
        deleted_assets = set()
        deleted_assets2 = set()
        sector_mapping = {
            'Financial Services': 'Finance',
            'Communication Services': 'Telecommunications',
            'Consumer Defensive': 'Consumer Staples',
            'Consumer Cyclical': 'Consumer Discretionary',
            None: 'Miscellaneous',  # Treat 'None' as 'Miscellaneous'
        }
        for asset in assets:
            try:
                test = yf.Ticker(asset.ticker)
                info = test.info

                if not info:
                    deleted_assets.add(asset.name)
                    asset.delete()
                    self.stdout.write(self.style.ERROR(f'Deleted asset due to missing data: {asset.ticker}'))
                    time.sleep(2)
                    continue
                
                # Update asset_type based on quoteType
                quote_type = info.get('quoteType')
                if quote_type == "EQUITY":
                    asset.asset_type = 'Stock'
                elif quote_type == "ETF":
                    asset.asset_type = 'ETF'
                else:
                    asset.delete()
                    deleted_assets2.add(asset.name)
                    self.stdout.write(self.style.ERROR(f'Deleted asset due to incompatible quoteType: {asset.ticker}'))
                    time.sleep(2)
                    continue
                
                # Update sector if it exists and is valid
                sector = info.get('sector')
                if sector in sector_mapping:  # Map sector to original if necessary
                    asset.sector = sector_mapping[sector]
                elif sector and sector in dict(Asset.SECTOR_CHOICES).values():  # Direct mapping if no need to adjust
                    asset.sector = sector
                elif sector == None:
                    asset.sector = 'Miscellaneous'
                else:
                    missing_sectors.add(sector)
                    self.stdout.write(self.style.WARNING(f'This asset ({asset.name}) does not have sector: {sector}'))
                
                # Update industry if it exists
                industry = info.get('industry')
                if industry:
                    asset.industry = industry
                
                asset.save()
                self.stdout.write(self.style.SUCCESS(f'Updated asset: {asset.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating asset {asset.name}: {str(e)}'))
        
        self.stdout.write(self.style.ERROR(f'These assets do not exist in yfinance:'))
        for asset in deleted_assets:
            self.stdout.write(self.style.ERROR(f'{asset}'))
        self.stdout.write(self.style.ERROR(f'These assets do not exist becase of index:'))
        for asset in deleted_assets2:
            self.stdout.write(self.style.ERROR(f'{asset}'))
        self.stdout.write(self.style.NOTICE(f'These sectors do not exist:'))
        for sector in missing_sectors:
            self.stdout.write(self.style.NOTICE(f'{sector}'))
