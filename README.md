# interpelly

*Interpelly* è un progetto open source che raccoglie gli interpelli scolastici e notifica i nuovi annunci su Telegram.
*Al momento il progetto è attivo solo per la Lombardia.*

## Avvio

```sh
uv sync
cp .env.example .env
uv run python src/manage.py migrate
uv run python src/manage.py createsuperuser
uv run python src/manage.py collectstatic --noinput
uv run python src/manage.py runserver
```

Configura `.env` con il token del bot e l'ID del supergruppo Telegram. Il gruppo deve avere gli argomenti attivati e il bot deve poterli gestire e inviare messaggi.

L'admin è disponibile su `http://127.0.0.1:8000/admin/`.
Il database SQLite è in `src/db.sqlite3`.

## Comandi

```sh
uv run python src/manage.py update_provinces
uv run python src/manage.py init_threads
uv run python src/manage.py scrape_interpelli
uv run python src/manage.py notify_interpelli
```

Le nuove province sono inattive. Gli aggiornamenti preservano l'attivazione e gli ID dei thread. Le province inattive sono escluse da scraping, creazione dei thread e notifiche.

Gli interpelli sono identificati dall'URL e non vengono eliminati quando scompaiono dal sito. `created_at` indica la prima acquisizione, `updated_at` l'ultimo scraping in cui sono stati ritrovati. `last_scraped_at` della provincia cambia solo dopo uno scraping riuscito.

Ogni interpello genera un messaggio nel thread della provincia. Solo gli invii riusciti aggiornano `notified`, `notified_at` e `telegram_message_id`. Errori e thread mancanti lasciano le notifiche pendenti. Gli aggiornamenti agli annunci già notificati non generano altri messaggi.
