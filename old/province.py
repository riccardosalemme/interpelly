# Pagina principale
# https://www.mim.gov.it/web/usr-lombardia/interpelli-ricerca-supplenti

import requests
from rich import print
from parsel import Selector

response = requests.get("https://www.mim.gov.it/web/usr-lombardia/interpelli-ricerca-supplenti")
response.raise_for_status()
sel = Selector(text=response.text)
links = sel.css('a[href^="/web/"][href*="interpelli-ricerca-supplenti"]::attr(href)').getall()
links = [f"https://www.mim.gov.it{link}" for link in links]

print(links)

with open("province.txt", "w") as f:
    for link in links:
        f.write(link + "\n")