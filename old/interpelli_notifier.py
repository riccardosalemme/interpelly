from datetime import datetime
import json
import os
from parsel import Selector
import requests
from rich import print
from notifier import send_interpelli_telegram
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

MESI_ITA = {
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12,
}

def parse_data_italiana(data_str):
    try:
        parti = data_str.strip().lower().split()
        giorno = int(parti[0])
        mese = MESI_ITA[parti[1]]
        anno = int(parti[2])
        return datetime(anno, mese, giorno).strftime(
            "%Y-%m-%d"
        )
    except (IndexError, KeyError, ValueError):
        return None

def get_provincia_from_link(link):
    return (
        link.replace("/interpelli-ricerca-supplenti", "")
        .replace("https://www.mim.gov.it/web/", "")
        .upper()
        .replace("-", " ")
    )


interpelli_esistenti = []
link_esistenti = set()

if os.path.exists("interpelli.json"):
    with open("interpelli.json", "r", encoding="utf-8") as f:
        try:
            interpelli_esistenti = json.load(f)
            link_esistenti = {item["link"] for item in interpelli_esistenti}
        except json.JSONDecodeError:
            interpelli_esistenti = []

with open("province_interesse.txt", "r") as f:
    province = [line.strip() for line in f.readlines()]

nuovi_interpelli = []


for provincia in province:
    print(
        f"[bold blue]Elaborazione della provincia:[/bold blue] {get_provincia_from_link(provincia)}"
    )
    response = requests.get(provincia)
    response.raise_for_status()
    sel = Selector(text=response.text)

    for article in sel.css("article.article"):
        link = article.css("h3 a::attr(href)").get(default="").strip()

        if link and link not in link_esistenti:
            data = article.css(".article_data::text").get(default="").strip()
            istituto = article.css("h3 a::text").get(default="").strip()
            descrizione = (
                article.css("div.article_wrapper > p::text")
                .get(default="")
                .strip()
            )

            nuovo_item = {
                "data": parse_data_italiana(data),
                "title": istituto,
                "descrizione": descrizione,
                "link": link,
                "provincia": get_provincia_from_link(provincia),
            }

            nuovi_interpelli.append(nuovo_item)
            link_esistenti.add(link)

print(f"\n[bold green]Trovati {len(nuovi_interpelli)} nuovi interpelli![/bold green]")


if nuovi_interpelli:
    tutti_gli_interpelli = interpelli_esistenti + nuovi_interpelli
    with open("interpelli.json", "w", encoding="utf-8") as f:
        json.dump(
            tutti_gli_interpelli, f, ensure_ascii=False, indent=4, default=str
        )
        
    BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

    print("[bold yellow]Invio notifiche su Telegram in corso...[/bold yellow]")
    sent_count = asyncio.run(
        send_interpelli_telegram(
            bot_token=BOT_TOKEN,
            chat_id=CHAT_ID,
            interpelli=nuovi_interpelli,
        )
    )
    print(
        f"[bold green]Inviati {sent_count} messaggi su Telegram![/bold green]"
    )