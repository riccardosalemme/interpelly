import asyncio
from html import escape

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from asgiref.sync import async_to_sync, sync_to_async
from django.conf import settings
from django.utils import timezone
from rich import print

from .models import Interpello, Province


def _text_length(text):
    return len(text.encode("utf-16-le")) // 2


def _truncate(text, limit):
    if _text_length(text) <= limit:
        return text
    return text.encode("utf-16-le")[: (limit - 1) * 2].decode("utf-16-le", errors="ignore") + "…"


def format_interpello_msg(item):
    link_text = "Apri sul sito MIM"
    budget = 4096 - _text_length(link_text) - 4
    title = _truncate(item.title or "Titolo non specificato", 1024)
    description = _truncate(
        item.description or "Nessuna descrizione specificata.",
        budget - _text_length(title),
    )
    return (
        f"<b>{escape(title)}</b>\n\n"
        f"<i>{escape(description)}</i>\n\n"
        f'<a href="{escape(item.url, quote=True)}">{link_text}</a>'
    )


async def _request(method, **kwargs):
    for attempt in range(3):
        try:
            return await method(**kwargs)
        except TelegramRetryAfter as error:
            if attempt == 2 or error.retry_after > 60:
                raise
            await asyncio.sleep(max(0, error.retry_after))


def init_threads():
    provinces = list(Province.objects.filter(active=True, telegram_thread_id__isnull=True))
    if not provinces:
        return 0
    return async_to_sync(_init_threads)(provinces)


async def _init_threads(provinces):
    count = 0
    async with Bot(token=settings.TELEGRAM_BOT_TOKEN) as bot:
        for province in provinces:
            try:
                topic = await _request(
                    bot.create_forum_topic,
                    chat_id=settings.TELEGRAM_CHAT_ID,
                    name=_truncate(province.name, 128),
                )
            except TelegramAPIError as error:
                print(f"[red]Errore creazione thread per {province.name}: {error}[/red]")
                continue
            province.telegram_thread_id = topic.message_thread_id
            await sync_to_async(province.save)(update_fields=["telegram_thread_id", "updated_at"])
            count += 1
    return count


def notify_interpelli():
    items = list(
        Interpello.objects.filter(notified=False, province__active=True)
        .select_related("province")
        .order_by("created_at", "pk")
    )
    if not items:
        return 0
    return async_to_sync(_notify_interpelli)(items)


def _mark_notified(item_id, message_id):
    # QuerySet.update deliberately leaves the last scraping timestamp untouched.
    Interpello.objects.filter(pk=item_id).update(
        notified=True,
        notified_at=timezone.now(),
        telegram_message_id=message_id,
    )


async def _notify_interpelli(items):
    count = 0
    async with Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=False),
    ) as bot:
        for item in items:
            if item.province.telegram_thread_id is None:
                print(f"[yellow]Thread mancante per {item.province.name}: salto {item.url}[/yellow]")
                continue
            try:
                message = await _request(
                    bot.send_message,
                    chat_id=settings.TELEGRAM_CHAT_ID,
                    message_thread_id=item.province.telegram_thread_id,
                    text=format_interpello_msg(item),
                )
            except TelegramAPIError as error:
                print(f"[red]Errore invio interpello {item.url}: {error}[/red]")
                continue
            await sync_to_async(_mark_notified)(item.pk, message.message_id)
            count += 1
            await asyncio.sleep(0.5)
    return count
