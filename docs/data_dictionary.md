# Data Dictionary

| Table | Field | Definition |
|---|---|---|
| raw.raw_product_item | raw_id | Surrogate key for captured evidence |
| raw.raw_product_item | source | Domain or channel identifier |
| raw.raw_product_item | external_id | Source-native product identity |
| raw.raw_product_item | price | Decimal price parsed from public source |
| raw.raw_product_item | raw_payload | Original semantic payload |
| raw.raw_product_item | crawl_fingerprint | SHA-256 identity/price/availability/rating |
| dim.dim_product | product_key | Warehouse product surrogate key |
| dim.dim_date | date_key | `YYYYMMDD` integer key |
| dwd.fact_price_snapshot | fact_id | Atomic observation key |
| dws.product_daily_price | avg_price | Arithmetic mean of daily observations |
| dws.product_daily_price | last_price | Latest observation of the day |
| ads.price_anomaly | change_rate | `(current_price - previous_price) / previous_price` |

## Metrics

- **Average price** = `AVG(price)` over the selected date grain.
- **Price change rate** = `(current_price - previous_price) / previous_price`.
- **Anomaly** = absolute price change rate >= 5%.
- **Out-of-stock rate** = `out_of_stock_count / total_snapshot_count`.
- **Category price index** = average product price by category and date.
