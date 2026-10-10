.PHONY: setup init-db crawl etl quality-report api scheduler test lint

setup:
	powershell -ExecutionPolicy Bypass -File scripts/setup_python.ps1

init-db:
	docker compose exec -T mysql mysql -uroot -p$${MYSQL_ROOT_PASSWORD:-change_me_root} price_monitor < db/init/001_init.sql

crawl:
	python -m src.crawler.run_crawler

etl:
	python -m src.etl.run_etl

quality-report:
	python -m src.quality.run_quality

api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000

scheduler:
	python -m src.scheduler.main

test:
	pytest --cov=src --cov-report=term-missing

lint:
	ruff check src tests
	mypy src
