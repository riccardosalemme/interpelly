from django.core.management.base import BaseCommand

from interpelli.scraper import scrape_interpelli


class Command(BaseCommand):
    help = "Scarica e aggiorna gli interpelli delle province attive."

    def handle(self, *args, **options):
        scrape_interpelli()
