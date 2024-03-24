from django.core.management.base import BaseCommand
from app.models import Asset
from django.db.models import Q

class Command(BaseCommand):
    help = 'Updates "Health Care" sector values to "Healthcare"'

    def handle(self, *args, **kwargs):
        # Filter assets with the old sector value and update them
        updated_count = Asset.objects.filter(sector='Health Care').update(sector='Healthcare')
        
        # Print out the result
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} assets to "Healthcare" sector.'))