# Deployment and Operations

## Local Deployment

```bash
git clone <repository-url>
cd ecommerce-price-monitor
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Update `.env`, then:

```bash
docker compose up -d mysql redis
docker compose exec -T mysql mysql -uroot -p"$MYSQL_ROOT_PASSWORD" price_monitor < db/init/001_init.sql
docker compose up -d --build
make crawl
make etl
make quality-report
```

## Playwright

Playwright is optional and disabled by default. To install the browser runtime locally:

```bash
powershell -ExecutionPolicy Bypass -File scripts/setup_python.ps1 -Playwright
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m playwright install chromium
```

Enable it in `.env`:

```bash
PLAYWRIGHT_ENABLED=1
PLAYWRIGHT_BROWSER=chromium
```

For Docker builds that need Playwright:

```bash
docker build --build-arg INSTALL_PLAYWRIGHT=1 -t ecommerce-price-monitor-playwright .
```

## Metabase

1. Open http://localhost:3000.
2. Complete admin setup.
3. Add MySQL using the read-only `metabase` account.
4. Import `config/metabase_model.yml` as the semantic reference.

## Airflow Migration

APScheduler calls independent Python modules. Replace scheduler jobs with Airflow operators while retaining the same commands and `max_active_runs=1`.
