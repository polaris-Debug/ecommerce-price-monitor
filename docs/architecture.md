# Architecture

```mermaid
flowchart LR
  A[Public sources<br/>Books to Scrape] --> B[Scrapy Collector<br/>rate limit, retry, robots]
  B --> C[(Raw Layer<br/>raw.raw_product_item)]
  D[API Event ingestion] --> C
  C --> E[ETL / SQL transform<br/>idempotent]
  E --> F[(ODS)]
  E --> G[(DWD facts)]
  E --> H[(DWS metrics)]
  E --> I[(ADS anomalies)]
  G --> J[FastAPI]
  H --> K[Metabase]
  I --> L[Alert webhook]
  M[APScheduler] --> B
  M --> E
  M --> N[Data quality report]
  N --> L
```

## Layers

| Layer | Purpose | Pattern |
|---|---|---|
| Raw | Immutable source evidence | append-only, unique fingerprint |
| ODS | Typed and deduplicated snapshots | raw-id one-to-one |
| DIM | Product, category, date, source dimensions | slowly changing upsert |
| DWD | Atomic price snapshot facts | one row per capture |
| DWS | Daily aggregate metrics | upsert by date/product/source |
| ADS | Anomaly and business-facing tables | threshold detection |

## Runtime Components

- **collector**: Scrapy process; supports `JOBDIR` resume and AutoThrottle.
- **scheduler**: APScheduler; jobs call independent modules and can be moved to Airflow without code changes.
- **API**: FastAPI; supports near-real-time event ingestion and analytical reads.
- **MySQL**: system of record and warehouse.
- **Redis**: crawl deduplication and distributed execution lock storage.
- **Metabase**: dashboard and reporting layer with read-only database account.

## Data Governance

- `raw_payload` preserves original evidence.
- All transformations are idempotent and keyed by natural or surrogate keys.
- Secrets are environment-injected; `.env` is never committed.
- Data quality reports are stored in `reports/`.
