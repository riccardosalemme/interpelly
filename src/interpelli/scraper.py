from datetime import date
from urllib.parse import urljoin, urlparse

import requests
from django.db import transaction
from django.utils import timezone
from parsel import Selector
from rich import print

from .models import Interpello, Province


PROVINCES_URL = "https://www.mim.gov.it/web/usr-lombardia/interpelli-ricerca-supplenti"
ITALIAN_MONTHS = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
}


def parse_italian_date(value):
    try:
        day, month, year = value.strip().lower().split()
        return date(int(year), ITALIAN_MONTHS[month], int(day))
    except (ValueError, KeyError):
        return None


def update_provinces():
    response = requests.get(PROVINCES_URL, timeout=30)
    response.raise_for_status()
    selector = Selector(text=response.text)
    links = selector.css(
        'a[href*="/web/"][href*="interpelli-ricerca-supplenti"]::attr(href)'
    ).getall()
    count = 0
    for url in dict.fromkeys(urljoin(response.url, link.strip()) for link in links):
        parts = urlparse(url).path.strip("/").split("/")
        if (
            urlparse(url).netloc != urlparse(PROVINCES_URL).netloc
            or len(parts) != 3
            or parts[0] != "web"
            or parts[1] == "usr-lombardia"
            or parts[2] != "interpelli-ricerca-supplenti"
        ):
            continue
        name = parts[1].replace("-", " ").upper()
        Province.objects.update_or_create(url=url, defaults={"name": name})
        count += 1
    print(f"[bold green]Aggiornate {count} province![/bold green]")
    return count


def scrape_interpelli():
    count = 0
    for province in Province.objects.filter(active=True):
        print(f"[bold blue]Elaborazione della provincia:[/bold blue] {province.name}")
        try:
            response = requests.get(province.url, timeout=30)
            response.raise_for_status()
            selector = Selector(text=response.text)
            province_count = 0
            with transaction.atomic():
                for article in selector.css("article.article"):
                    link = article.css("h3 a::attr(href)").get(default="").strip()
                    if not link:
                        continue
                    _, created = Interpello.objects.update_or_create(
                        url=urljoin(response.url, link),
                        defaults={
                            "province": province,
                            "published_date": parse_italian_date(
                                article.css(".article_data::text").get(default="")
                            ),
                            "title": article.css("h3 a").xpath("string(.)").get(default="").strip(),
                            "description": " ".join(
                                article.css("div.article_wrapper > p").xpath("string(.)").getall()
                            ).strip(),
                            "updated_at": timezone.now(),
                        },
                    )
                    if created:
                        province_count += 1
                province.last_scraped_at = timezone.now()
                province.save(update_fields=["last_scraped_at", "updated_at"])
            count += province_count
            print(f"[bold green]{province.name}: trovati {province_count} nuovi interpelli![/bold green]")
        except Exception as error:
            print(f"[red]Errore durante lo scraping di {province.name}: {error}[/red]")
    print(f"\n[bold green]Trovati {count} nuovi interpelli in totale![/bold green]")
    return count
