from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from interpelli.telegram import init_threads


class Command(BaseCommand):
    help = "Crea i thread Telegram mancanti per le province attive."

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            raise CommandError("Configura TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID nel file .env.")
        count = init_threads()
        self.stdout.write(self.style.SUCCESS(f"Creati {count} thread."))
