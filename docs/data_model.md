# Data Model and ER Diagram

```mermaid
erDiagram
  RAW_PRODUCT_ITEM ||--|| ODS_PRODUCT_SNAPSHOT : raw_id
  ODS_PRODUCT_SNAPSHOT ||--|| FACT_PRICE_SNAPSHOT : ods_raw_id
  DIM_PRODUCT ||--o{ FACT_PRICE_SNAPSHOT : product_key
  DIM_CATEGORY ||--o{ FACT_PRICE_SNAPSHOT : category_key
  DIM_DATE ||--o{ FACT_PRICE_SNAPSHOT : snapshot_date_key
  DIM_PRODUCT ||--o{ PRODUCT_DAILY_PRICE : product_key
  DIM_DATE ||--o{ PRODUCT_DAILY_PRICE : date_key
  DIM_PRODUCT ||--o{ PRICE_ANOMALY : product_key
  DIM_DATE ||--o{ PRICE_ANOMALY : date_key
```

## Grain

- `raw_product_item`: one captured source response.
- `ods_product_snapshot`: one cleaned source response.
- `fact_price_snapshot`: one product price observation.
- `product_daily_price`: one product/source/day.
- `price_anomaly`: one product/source/day when change rate is at least 5%.
