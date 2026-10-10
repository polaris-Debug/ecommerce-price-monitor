# E-commerce Price & Competitor Monitor

An enterprise-grade, reproducible analytics pipeline for monitoring public competitor product prices:

`collection -> raw -> clean -> warehouse model -> metrics -> API/dashboard -> quality report -> alerting`

The project uses Python, MySQL, Scrapy, optional Playwright, Redis, SQLAlchemy, APScheduler, FastAPI, Metabase, Docker, and GitHub Actions.

## Quick Start

```bash
powershell -ExecutionPolicy Bypass -File scripts/setup_python.ps1
.\.venv\Scripts\Activate.ps1
cp .env.example .env
docker compose up -d mysql redis
make init-db
docker compose up -d --build
make crawl
make etl
make quality-report
```

- API: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- Metabase: http://localhost:3000

## Documentation

- [Architecture](docs/architecture.md)
- [Data model and ER diagram](docs/data_model.md)
- [Deployment](docs/deployment.md)
- [Data dictionary](docs/data_dictionary.md)
- [Operations runbook](docs/runbook.md)
