ETL_STATEMENTS = [
    """
    INSERT INTO etl.job_run (job_name, status, started_at)
    VALUES ('daily_price_etl', 'running', UTC_TIMESTAMP())
    """,
    """
    INSERT INTO ods.ods_product_snapshot
      (raw_id, source, external_id, url, product_name, category_name, price, currency,
       availability, rating, raw_payload, captured_at, batch_id)
    SELECT r.raw_id, r.source, r.external_id, r.url, r.name, r.category_name, r.price, r.currency,
           r.availability, r.rating, r.raw_payload, r.captured_at, r.batch_id
    FROM raw.raw_product_item r
    LEFT JOIN ods.ods_product_snapshot o ON o.raw_id = r.raw_id
    WHERE o.raw_id IS NULL
    """,
    """
    INSERT INTO dim.dim_category (category_name)
    SELECT DISTINCT TRIM(category_name)
    FROM ods.ods_product_snapshot
    WHERE TRIM(category_name) <> ''
    ON DUPLICATE KEY UPDATE category_name = VALUES(category_name)
    """,
    """
    INSERT INTO dim.dim_product
      (source, external_id, product_name, product_url, first_seen_at, last_seen_at)
    SELECT o.source, o.external_id, MAX(o.product_name), MAX(o.url),
           MIN(o.captured_at), MAX(o.captured_at)
    FROM ods.ods_product_snapshot o
    GROUP BY o.source, o.external_id
    ON DUPLICATE KEY UPDATE
      product_name = VALUES(product_name), product_url = VALUES(product_url),
      last_seen_at = VALUES(last_seen_at)
    """,
    """
    INSERT INTO dim.dim_date (date_key, calendar_date, year, month, day, week_of_year, weekday)
    SELECT DISTINCT DATE_FORMAT(captured_at, '%Y%m%d'), DATE(captured_at),
           YEAR(captured_at), MONTH(captured_at),
           DAY(captured_at), WEEK(captured_at, 3), WEEKDAY(captured_at)
    FROM ods.ods_product_snapshot
    ON DUPLICATE KEY UPDATE calendar_date = VALUES(calendar_date)
    """,
    """
    INSERT INTO dwd.fact_price_snapshot
      (snapshot_date_key, product_key, category_key, source, price, availability, rating, ods_raw_id)
    SELECT d.date_key, p.product_key, c.category_key, o.source, o.price, o.availability, o.rating, o.raw_id
    FROM ods.ods_product_snapshot o
    JOIN dim.dim_date d ON d.calendar_date = DATE(o.captured_at)
    JOIN dim.dim_product p ON p.source = o.source AND p.external_id = o.external_id
    LEFT JOIN dim.dim_category c ON c.category_name = TRIM(o.category_name)
    LEFT JOIN dwd.fact_price_snapshot f ON f.ods_raw_id = o.raw_id
    WHERE f.ods_raw_id IS NULL
    """,
    """
    INSERT INTO dws.product_daily_price
      (date_key, product_key, source, min_price, max_price, avg_price, last_price, snapshot_count)
    SELECT snapshot_date_key, product_key, source, MIN(price), MAX(price), ROUND(AVG(price), 4),
           SUBSTRING_INDEX(GROUP_CONCAT(price ORDER BY ods_raw_id DESC), ',', 1), COUNT(*)
    FROM dwd.fact_price_snapshot
    GROUP BY snapshot_date_key, product_key, source
    ON DUPLICATE KEY UPDATE
      min_price = VALUES(min_price), max_price = VALUES(max_price), avg_price = VALUES(avg_price),
      last_price = VALUES(last_price), snapshot_count = VALUES(snapshot_count)
    """,
    """
    INSERT INTO ads.price_anomaly
      (date_key, product_key, source, current_price, previous_price, change_rate, anomaly_type)
    SELECT cur.date_key, cur.product_key, cur.source, cur.last_price, prev.last_price,
           ROUND((cur.last_price - prev.last_price) / NULLIF(prev.last_price, 0), 4),
           IF(cur.last_price < prev.last_price, 'price_drop', 'price_increase')
    FROM dws.product_daily_price cur
    JOIN dws.product_daily_price prev
      ON prev.product_key = cur.product_key AND prev.source = cur.source
     AND prev.date_key = (SELECT MAX(date_key) FROM dws.product_daily_price x
                          WHERE x.product_key = cur.product_key AND x.source = cur.source
                            AND x.date_key < cur.date_key)
    LEFT JOIN ads.price_anomaly existing
      ON existing.date_key = cur.date_key AND existing.product_key = cur.product_key
     AND existing.source = cur.source
    WHERE existing.product_key IS NULL
      AND ABS((cur.last_price - prev.last_price) / NULLIF(prev.last_price, 0)) >= 0.05
    """,
    """
    UPDATE etl.job_run
    SET status='succeeded', finished_at=UTC_TIMESTAMP()
    WHERE job_name='daily_price_etl' AND status='running'
    """,
]
