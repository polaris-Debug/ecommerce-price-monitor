# Operations Runbook

## Health

```bash
curl http://localhost:8000/health
docker compose ps
docker compose logs -f api scheduler
```

## Crawler Failure

1. Inspect logs and `jobs/crawler`.
2. Confirm robots.txt and target availability.
3. Reduce `CONCURRENT_REQUESTS` or increase `DOWNLOAD_DELAY`.
4. Resume with `make crawl`.
5. If the target is unavailable, add a compliant public-source spider.

## ETL Failure

1. Query `etl.job_run`.
2. Confirm ODS `raw_id` uniqueness.
3. Re-run `make etl`.
4. Run `make quality-report`.

## Security

- Rotate database and API secrets.
- Use a secrets manager in production.
- Keep the Metabase account read-only.
- Put API behind TLS and an authenticating gateway.
