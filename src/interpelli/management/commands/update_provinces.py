from django.core.management.base import BaseCommand, CommandError
from requests import RequestException

from interpelli.scraper import update_provinces


class Command(BaseCommand):
    help = "Scarica e aggiorna le province della Lombardia."

    def handle(self, *args, **options):
        try:
            update_provinces()
        except RequestException as error:
            raise CommandError(str(error)) from error
