# Pagina elenco interpelli
# https://www.mim.gov.it/web/ <PROVINCIA> /interpelli-ricerca-supplenti

import requests
from rich import print
from datetime import datetime
from parsel import Selector
import json

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
        return datetime(anno, mese, giorno).date()
    except (IndexError, KeyError, ValueError):
        return None

def get_provincia_from_link(link):
    return link.replace("/interpelli-ricerca-supplenti", "").replace("https://www.mim.gov.it/web/", "").upper().replace("-", " ")


with open("province_interesse.txt", "r") as f:
    province = [line.strip() for line in f.readlines()]
    
interpelli = []    

for provincia in province:
    print(
        f"[bold blue]Elaborazione della provincia:[/bold blue] {get_provincia_from_link(provincia)}"
    )
    response = requests.get(provincia)
    response.raise_for_status()
    sel = Selector(text=response.text)

    for article in sel.css("article.article"):
        data = article.css(".article_data::text").get(default="").strip()
        link = article.css("h3 a::attr(href)").get(default="").strip()
        istituto = article.css("h3 a::text").get(default="").strip()
        descrizione = article.css("div.article_wrapper > p::text").get(default="").strip()

        interpelli.append({
            "data": parse_data_italiana(data),
            "title": istituto,
            "descrizione": descrizione,
            "link": link,
            "provincia": get_provincia_from_link(provincia)
        })

print(f"\n[bold green]Trovati {len(interpelli)} interpelli![/bold green]")

with open("interpelli.json", "w") as f:
    json_data = json.dumps(interpelli, default=str, ensure_ascii=False, indent=4)
    f.write(json_data)