from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from interpelli.telegram import notify_interpelli


class Command(BaseCommand):
    help = "Invia gli interpelli non notificati nei thread delle province attive."

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            raise CommandError("Configura TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID nel file .env.")
        count = notify_interpelli()
        self.stdout.write(self.style.SUCCESS(f"Inviati {count} messaggi."))
