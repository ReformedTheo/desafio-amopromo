from django.core.management.base import BaseCommand
from core.services import import_airports_from_api

class Command(BaseCommand):
    help = 'Fetches the latest airport data from the API and updates the local database.'

    def handle(self, *args, **options):
        self.stdout.write("Starting airport import process...")
        
        result = import_airports_from_api()

        if result['status'] == 'SUCCESS':
            self.stdout.write(self.style.SUCCESS(
                f"Import completed successfully! "
                f"Created: {result['created']}, Updated: {result['updated']}."
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"Import failed. Details: {result['details']}"
            ))